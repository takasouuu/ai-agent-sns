"""
investment_agent/agent.py
投資系X投稿 SNS エージェント — メインエントリポイント

使い方（CLI）:
  # 岐阜暴威ライブ配信の動画から投稿案を生成
  python -m investment_agent.agent video \
      --url "https://www.youtube.com/watch?v=XXXXXXXXX" \
      --source gifuboui

  # 楽待チャンネル株関連回から投稿案を生成
  python -m investment_agent.agent video \
      --url "https://www.youtube.com/watch?v=XXXXXXXXX" \
      --source rakumachi_stock

  # X/Twitter トレンドニュースから投稿案を生成（dry_run でAPIキー不要）
  python -m investment_agent.agent news [--dry-run]
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import subprocess
import sys
from datetime import date
from pathlib import Path
from typing import Any

# ── パッケージルートを sys.path に追加（-m 実行以外でも動作するように）──
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from investment_agent.config import (
    CHANNELS,
    NUM_SETS,
    OUT_ROOT,
    SHOTS_PER_SET,
    TMP,
    YT_DLP_OPTS,
    YT_DLP_VIDEO_OPTS,
)
from investment_agent.news_fetcher import fetch_investment_news
from investment_agent.post_builder import build_news_posts, build_video_posts

logging.basicConfig(format="%(levelname)s %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════
# ユーティリティ
# ══════════════════════════════════════════════════════════════
def sanitize(text: str, max_len: int = 60) -> str:
    text = re.sub(r"[\s/\\:*?\"<>|]+", "_", text.strip())
    return text[:max_len]


def to_seconds(ts: str) -> float:
    ts = ts.replace(",", ".")
    parts = ts.split(":")
    if len(parts) == 3:
        h, m, s = parts
        return int(h) * 3600 + int(m) * 60 + float(s)
    elif len(parts) == 2:
        m, s = parts
        return int(m) * 60 + float(s)
    return float(ts)


def parse_vtt_cues(vtt_path: Path) -> list[tuple[float, str]]:
    """VTT ファイルを解析して (秒, テキスト) のリストを返す"""
    lines = vtt_path.read_text(errors="ignore").splitlines()
    cues: list[tuple[float, str]] = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if "-->" in line:
            start = line.split("-->", 1)[0].strip()
            i += 1
            text_lines: list[str] = []
            while i < len(lines) and lines[i].strip():
                t = re.sub(r"<[^>]+>", "", lines[i]).strip()
                if t and t not in ("Kind: captions", "Language: ja"):
                    text_lines.append(t)
                i += 1
            text = " ".join(text_lines)
            if text:
                cues.append((to_seconds(start), text))
        i += 1
    return cues


def pick_shot_times(
    cues: list[tuple[float, str]],
    keywords: list[str],
    duration: float,
    num_sets: int = NUM_SETS,
    shots_per_set: int = SHOTS_PER_SET,
) -> list[list[tuple[float, str]]]:
    """
    動画を num_sets 区間に分割し、各区間から shots_per_set 枚分の
    タイムスタンプを選んで返す。
    キーワードを含む字幕を優先してアンカーとする。
    """
    bucket_size = duration / num_sets
    result: list[list[tuple[float, str]]] = []

    for idx in range(num_sets):
        b_start = idx * bucket_size
        b_end   = (idx + 1) * bucket_size
        bucket  = [(s, t) for s, t in cues if b_start <= s < b_end]
        kw_hits = [(s, t) for s, t in bucket if any(k in t for k in keywords)]
        anchor  = kw_hits if kw_hits else bucket

        if anchor:
            start_sec = max(2.0, anchor[0][0])
        else:
            start_sec = max(2.0, (b_start + b_end) / 2)

        after = [(s, t) for s, t in cues if s >= start_sec]
        picks = after[:shots_per_set]

        # 足りない場合はパディング
        while len(picks) < shots_per_set:
            last = picks[-1][0] if picks else start_sec
            picks.append((last + 3.0, ""))

        result.append(picks)

    return result


def run_ffmpeg(video_path: Path, vtt_path: Path, sec: float, out_path: Path) -> None:
    """字幕を合成したスクリーンショットを生成する"""
    cmd = [
        "ffmpeg", "-y",
        "-ss", f"{sec:.2f}",
        "-i", str(video_path),
        "-vf", f"subtitles={vtt_path.name}",
        "-frames:v", "1",
        str(out_path),
    ]
    subprocess.run(cmd, cwd=str(vtt_path.parent), check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def run_ytdlp(url: str, out_dir: Path, with_video: bool = True) -> dict[str, Any]:
    """
    yt-dlp で動画情報・字幕・本体（オプション）をダウンロードし、
    {video_id, title, duration, info_path, vtt_path, video_path} を返す。
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    opts = YT_DLP_VIDEO_OPTS if with_video else YT_DLP_OPTS

    cmd = ["yt-dlp"] + opts + ["-P", str(out_dir), url]
    logger.info("yt-dlp 実行中: %s", url)
    subprocess.run(cmd, check=True)

    # info.json を探す
    info_paths = list(out_dir.glob("*.info.json"))
    if not info_paths:
        raise FileNotFoundError(f"info.json が見つかりません: {out_dir}")
    info_path = info_paths[0]
    info = json.loads(info_path.read_text())

    video_id = info.get("id", info_path.stem.replace(".info", ""))
    title    = info.get("title", "動画")
    duration = float(info.get("duration") or 1200)

    # VTT を探す
    vtt_candidates = list(out_dir.glob("*.ja.vtt")) + list(out_dir.glob("*.ja-JP.vtt"))
    vtt_path = vtt_candidates[0] if vtt_candidates else None

    # 動画ファイルを探す
    video_path = None
    if with_video:
        for ext in [".webm", ".mp4", ".mkv", ".m4v"]:
            candidates = list(out_dir.glob(f"*{ext}"))
            # info.json を除外
            candidates = [p for p in candidates if ".info" not in p.name]
            if candidates:
                video_path = candidates[0]
                break

    return {
        "video_id": video_id,
        "title": title,
        "duration": duration,
        "info_path": info_path,
        "vtt_path": vtt_path,
        "video_path": video_path,
    }


# ══════════════════════════════════════════════════════════════
# モード: video（岐阜暴威 / 楽待）
# ══════════════════════════════════════════════════════════════
def run_video_mode(url: str, source_key: str, fast: bool = False) -> None:
    """YouTube動画URLから5セットの投稿案＋スクショを生成する"""
    if source_key not in CHANNELS:
        raise ValueError(f"未知のソースキー: {source_key}. 選択肢: {list(CHANNELS.keys())}")

    channel = CHANNELS[source_key]
    channel_name = channel["name"]
    keywords     = channel["keywords"]
    label        = channel["label"]

    # ── ダウンロード ──────────────────────────────────────────
    tmp_dir = TMP / source_key
    dl_info = run_ytdlp(url, tmp_dir, with_video=(not fast))

    video_id   = dl_info["video_id"]
    title      = dl_info["title"]
    duration   = dl_info["duration"]
    vtt_path   = dl_info["vtt_path"]
    video_path = dl_info["video_path"]

    if vtt_path is None or not vtt_path.exists():
        logger.warning("日本語字幕が見つかりません。スクショはスキップします。")
        vtt_path = None

    # ── 出力ディレクトリ ──────────────────────────────────────
    today     = date.today().strftime("%Y-%m-%d")
    dir_name  = f"{today}_{sanitize(title)}_{video_id}"
    base_dir  = OUT_ROOT / dir_name
    base_dir.mkdir(parents=True, exist_ok=True)

    # ── 字幕解析 ──────────────────────────────────────────────
    cues: list[tuple[float, str]] = []
    all_shot_sets: list[list[tuple[float, str]]] = [[] for _ in range(NUM_SETS)]
    cues_summary: list[str] = []

    if vtt_path:
        cues = parse_vtt_cues(vtt_path)
        all_shot_sets = pick_shot_times(cues, keywords, duration)
        # 投稿文用の字幕要約（キーワード含む行を最大10件）
        kw_cues = [(s, t) for s, t in cues if any(k in t for k in keywords)][:10]
        cues_summary = [t for _, t in kw_cues]

    # ── 投稿案生成 ────────────────────────────────────────────
    source_basis = (
        "字幕内のキーワード頻出区間および話者熱量の高い区間より抽出"
        "（X/Twitterコメント取得不可のため代替根拠使用）"
    )
    posts = build_video_posts(
        title=title,
        channel_name=channel_name,
        keywords=keywords,
        cues_summary=cues_summary,
        source_basis=source_basis,
    )

    # ── セット出力 ────────────────────────────────────────────
    for idx, post_item in enumerate(posts, start=1):
        variant_dir = base_dir / str(idx)
        variant_dir.mkdir(parents=True, exist_ok=True)

        # post.txt
        (variant_dir / "post.txt").write_text(post_item["post_text"], encoding="utf-8")

        # スクショ（video_path がある場合のみ）
        meta_lines: list[str] = []
        if video_path and vtt_path and idx - 1 < len(all_shot_sets):
            shot_picks = all_shot_sets[idx - 1]
            for shot_idx, (sec, text) in enumerate(shot_picks, start=1):
                out_png = variant_dir / f"screenshot{shot_idx}.png"
                try:
                    run_ffmpeg(video_path, vtt_path, sec, out_png)
                    meta_lines.append(f"screenshot{shot_idx}.png: {sec:.1f}s / {text[:80]}")
                except subprocess.CalledProcessError as e:
                    logger.warning("スクショ生成失敗 set=%d shot=%d sec=%.1f: %s", idx, shot_idx, sec, e)
        else:
            meta_lines.append("（动画ファイルなし: --fast モードまたは字幕未取得のためスクショをスキップ）")

        (variant_dir / "screenshots_meta.txt").write_text("\n".join(meta_lines) + "\n", encoding="utf-8")

    # ── video_info.txt ────────────────────────────────────────
    (base_dir / "video_info.txt").write_text(
        f"video_id: {video_id}\n"
        f"title: {title}\n"
        f"url: {url}\n"
        f"channel: {channel_name}（{label}）\n"
        f"duration: {duration:.0f}s\n"
        f"generated: {today}\n"
        f"source_key: {source_key}\n"
        "コメント情報: 取得不可のため字幕の繰り返し言及・キーワード頻出区間を代替根拠として使用\n"
        f"投稿案数: {NUM_SETS}案（訴求軸ごとに1案）\n",
        encoding="utf-8",
    )

    print(f"[OK] {base_dir.name}")
    print(f"     投稿案: {NUM_SETS}セット → {base_dir}")


# ══════════════════════════════════════════════════════════════
# モード: news（X/Twitter トレンド速報）
# ══════════════════════════════════════════════════════════════
def run_news_mode(dry_run: bool = False) -> None:
    """X/Twitter トレンドから5セットのニュース速報投稿案を生成する"""
    logger.info("ニュース取得開始（dry_run=%s）", dry_run)
    news_items = fetch_investment_news(dry_run=dry_run)

    if not news_items:
        logger.error("ニュースアイテムが1件も取得できませんでした")
        return

    posts = build_news_posts(news_items)

    today    = date.today().strftime("%Y-%m-%d")
    dir_name = f"{today}_投資速報ニュース"
    base_dir = OUT_ROOT / dir_name
    base_dir.mkdir(parents=True, exist_ok=True)

    for idx, post_item in enumerate(posts, start=1):
        variant_dir = base_dir / str(idx)
        variant_dir.mkdir(parents=True, exist_ok=True)
        (variant_dir / "post.txt").write_text(post_item["post_text"], encoding="utf-8")
        # ニュース系はスクショなし
        (variant_dir / "screenshots_meta.txt").write_text(
            "（ニュースモードはスクリーンショットなし）\n", encoding="utf-8"
        )

    # ニュース元データを保存
    (base_dir / "news_source.json").write_text(
        json.dumps([{k: v for k, v in n.items() if k != "tweets"} for n in news_items],
                   ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    (base_dir / "video_info.txt").write_text(
        f"type: ニュース速報\n"
        f"source: X/Twitter API（投資関連キーワード検索）\n"
        f"generated: {today}\n"
        f"dry_run: {dry_run}\n"
        f"topics: {', '.join(n['topic'] for n in news_items)}\n"
        f"投稿案数: {len(posts)}案（訴求軸ごとに1案）\n",
        encoding="utf-8",
    )

    print(f"[OK] {base_dir.name}")
    print(f"     投稿案: {len(posts)}セット → {base_dir}")


# ══════════════════════════════════════════════════════════════
# CLI エントリポイント
# ══════════════════════════════════════════════════════════════
def main() -> None:
    parser = argparse.ArgumentParser(
        description="投資系X投稿 SNS エージェント",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = parser.add_subparsers(dest="mode", required=True)

    # ── video サブコマンド ────────────────────────────────────
    vp = sub.add_parser("video", help="YouTube動画から投稿案とスクショを生成")
    vp.add_argument("--url",    required=True,  help="YouTube動画URL")
    vp.add_argument(
        "--source",
        required=True,
        choices=list(CHANNELS.keys()),
        help=f"ソースキー: {list(CHANNELS.keys())}",
    )
    vp.add_argument(
        "--fast",
        action="store_true",
        help="動画本体をダウンロードせず投稿文のみ生成（スクショなし）",
    )

    # ── news サブコマンド ──────────────────────────────────────
    np = sub.add_parser("news", help="X/Twitterトレンドから投資速報投稿案を生成")
    np.add_argument(
        "--dry-run",
        action="store_true",
        help="APIを呼ばずモックデータで動作確認",
    )

    args = parser.parse_args()

    if args.mode == "video":
        run_video_mode(url=args.url, source_key=args.source, fast=args.fast)
    elif args.mode == "news":
        run_news_mode(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
