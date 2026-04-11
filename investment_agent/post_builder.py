"""
investment_agent/post_builder.py
投資系X投稿文（5訴求軸 × 1案）を生成するモジュール

post.txt フォーマット（仕様）
  --- より上     : そのままXに貼り付けられる投稿本文
  --- 以降       : 参考メタデータ（投稿時は削除）
"""

from __future__ import annotations

import textwrap
from typing import Any

from .config import AXES

# ──────────────────────────────────────────────────────────────
# 投資系ハッシュタグ共通2個（固定）
# ──────────────────────────────────────────────────────────────
HASHTAG_FIXED = "#投資 #株式投資"


# ──────────────────────────────────────────────────────────────
# ユーティリティ
# ──────────────────────────────────────────────────────────────
def _trim(text: str, max_len: int = 220) -> str:
    """本文が超過する場合に末尾を省略記号で切り詰める（140字超は意図的に許容）"""
    if len(text) <= max_len:
        return text
    return text[: max_len - 1] + "…"


def _format_post(body: str, axis: dict[str, Any]) -> str:
    """本文＋メタ情報を post.txt 形式に整形する"""
    hashtags = f"{HASHTAG_FIXED} {axis['hashtag_var']}"
    return (
        f"{body.strip()}\n"
        f"{hashtags}\n"
        "---\n"
        f"- 訴求軸: {axis['name']}\n"
        f"- 想定ターゲット: {axis['target']}\n"
        f"- CTA意図: {axis['cta']}\n"
        f"- 使用ハッシュタグ: {hashtags}\n"
    )


# ──────────────────────────────────────────────────────────────
# YouTube系（岐阜暴威 / 楽待）投稿生成
# ──────────────────────────────────────────────────────────────
def build_video_posts(
    title: str,
    channel_name: str,
    keywords: list[str],
    cues_summary: list[str],
    source_basis: str,
) -> list[dict[str, Any]]:
    """
    YouTube動画から5本の投稿案を生成する。

    Parameters
    ----------
    title        : 動画タイトル
    channel_name : "岐阜暴威" など
    keywords     : 動画固有キーワードリスト（最低3個）
    cues_summary : 字幕から抽出した重要発言要約リスト（最大10件）
    source_basis : "字幕（コメント取得不可）" など根拠説明

    Returns
    -------
    list of dict  各要素が 1セット情報
        {axis_id, post_text, kpi}
    """
    k = keywords
    kw0 = k[0] if len(k) > 0 else "投資"
    kw1 = k[1] if len(k) > 1 else "相場"
    kw2 = k[2] if len(k) > 2 else "戦略"

    # 字幕要約を1つの段落にまとめる（最大3行）
    excerpt = "／".join(cues_summary[:3]) if cues_summary else "（字幕要約なし）"

    posts = []

    # ── 軸1: 投資戦略・手法の具体性 ──────────────────────────────────────────
    body1 = textwrap.dedent(f"""\
        {channel_name}が語った「{kw0}」の使い方がとにかく実践的。

        ・{kw0}を使った具体的なエントリー条件とは
        ・「{excerpt[:30]}」という視点が刺さった
        ・{kw1}の流れを先読みするための着眼点

        再現性のある手法をまとめたい人は保存推奨。\
    """)
    posts.append(_build_result(1, body1, source_basis, "A/A/B/B/A"))

    # ── 軸2: リスク管理・メンタル ─────────────────────────────────────────────
    body2 = textwrap.dedent(f"""\
        {channel_name}の「損切りを迷わない理由」が正直すぎた。

        ・{kw1}局面での撤退基準の決め方
        ・含み損を抱えたときの思考の整理法
        ・「{kw2}」を守れれば感情は要らない

        メンタルで負ける前に保存を。あなたの経験と比べてみてほしい。\
    """)
    posts.append(_build_result(2, body2, source_basis, "A/B/A/A/B"))

    # ── 軸3: 銘柄・相場環境分析 ────────────────────────────────────────────────
    body3 = textwrap.dedent(f"""\
        {title} — 見逃した人のために要点を整理。

        ・注目の{kw0}銘柄とその選定根拠
        ・今の相場環境における{kw1}セクターの位置づけ
        ・{kw2}の動向から読み取れる次の一手

        判断の根拠を動画本編で確認してほしい。\
    """)
    posts.append(_build_result(3, body3, source_basis, "B/B/A/B/A"))

    # ── 軸4: 投資家の思考・哲学 ──────────────────────────────────────────────
    body4 = textwrap.dedent(f"""\
        「{excerpt[:40]}」

        {channel_name}のこの一言、ずっと頭に残っている。

        ・短期の損得より{kw2}という長期軸
        ・失敗を次の判断に変換するフレーム
        ・{kw0}に向き合い続けて見えてきたもの

        投資の哲学を言語化したい人は保存してみて。\
    """)
    posts.append(_build_result(4, body4, source_basis, "A/A/B/A/B"))

    # ── 軸5: 速報・ニュース活用 ───────────────────────────────────────────────
    body5 = textwrap.dedent(f"""\
        {channel_name}が{kw1}ニュースをどう投資に落とし込むか説明していた。

        ・速報が出た直後にまず確認すること
        ・{kw0}への影響を見極めるチェックポイント
        ・「{kw2}」軸でニュースを読む習慣が精度を上げる

        ニュース対応の型を持ちたい人は引用でコメントをどうぞ。\
    """)
    posts.append(_build_result(5, body5, source_basis, "B/B/B/A/A"))

    return posts


# ──────────────────────────────────────────────────────────────
# ニュース速報系投稿生成
# ──────────────────────────────────────────────────────────────
def build_news_posts(news_items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    X/Twitter トレンドから収集したニュースアイテムから5本の投稿案を生成する。

    Parameters
    ----------
    news_items : list of dict
        各要素 {topic, summary, tweets: [{"text":..., "created_at":...}], query}

    Returns
    -------
    list of dict（build_video_posts と同形式）
    """
    # 最大5トピックを各軸に割り当て（足りないときは同トピックを再利用）
    def _pick(idx: int) -> dict[str, Any]:
        return news_items[idx % len(news_items)] if news_items else {
            "topic": "投資情報",
            "summary": "ホットな投資情報が検出されませんでした",
            "tweets": [],
            "query": "",
        }

    posts = []

    for axis in AXES:
        item = _pick(axis["id"] - 1)
        topic   = item.get("topic", "投資情報")
        summary = item.get("summary", "")
        tweets  = item.get("tweets", [])
        # 代表ツイートを1件選ぶ（最多いいね or 先頭）
        rep_tweet = tweets[0]["text"][:60] if tweets else topic

        body = _make_news_body(axis, topic, summary, rep_tweet)
        basis = f"X/Twitter検索（クエリ: {item.get('query','')}）より上位ツイートを要約"
        posts.append(_build_result(axis["id"], body, basis, _news_kpi(axis["id"])))

    return posts


def _make_news_body(axis: dict, topic: str, summary: str, rep: str) -> str:
    """軸ごとに最適化したニュース速報投稿本文を返す"""
    axid = axis["id"]

    if axid == 1:
        return textwrap.dedent(f"""\
            【速報・手法】{topic}が市場を揺らしている。

            ・{summary[:50]}
            ・この局面でのエントリー判断ポイント
            ・ルールを守れば感情に振り回されない

            自分の投資ルールを見直すチャンス。保存して後で確認を。\
        """)
    elif axid == 2:
        return textwrap.dedent(f"""\
            【リスク】「{rep}」

            急変局面でのリスク管理を再確認。

            ・ポジションサイズを落とすタイミング
            ・{summary[:40]}という状況での損切り基準
            ・感情で動く前に確認すべきチェックリスト

            今の相場、どう乗り越えていますか？引用で教えてください。\
        """)
    elif axid == 3:
        return textwrap.dedent(f"""\
            {topic}——相場への影響を整理した。

            ・プラス影響が期待されるセクター
            ・{summary[:45]}という背景と注目銘柄
            ・過去の類似局面からの相場の反応パターン

            銘柄選定の参考にどうぞ。続報は動画・ポストで随時更新。\
        """)
    elif axid == 4:
        return textwrap.dedent(f"""\
            「{rep}」

            こういうニュースが出るたびに投資哲学が試される。

            ・短期ノイズに惑わされない判断軸の作り方
            ・{summary[:40]}を長期目線で見るとどう映るか
            ・ブレないための「自分ルール」を言語化しておく重要性

            あなたの投資哲学を引用で聞かせてください。\
        """)
    else:  # axid == 5
        return textwrap.dedent(f"""\
            ⚡ 速報まとめ：{topic}

            今Xで話題になっている投資ニュースのポイント。

            ・{summary[:55]}
            ・この情報の投資への即時示唆
            ・出遅れないために今確認すべきこと

            情報は早さより深さ。一緒に考えましょう。\
        """)


def _news_kpi(axis_id: int) -> str:
    table = {1: "A/A/B/A/B", 2: "A/B/A/A/B", 3: "B/A/A/B/A", 4: "A/A/B/A/C", 5: "A/B/B/A/A"}
    return table.get(axis_id, "B/B/B/B/B")


# ──────────────────────────────────────────────────────────────
# 共通ヘルパー
# ──────────────────────────────────────────────────────────────
def _build_result(axis_id: int, body: str, basis: str, kpi: str) -> dict[str, Any]:
    axis = AXES[axis_id - 1]
    post_text = _format_post(body, axis)
    post_text += (
        f"- 事実根拠（字幕/ニュース要約）: {basis}\n"
        f"- KPI自己評価（フック/保存/共感/会話/遷移）: {kpi}\n"
    )
    return {
        "axis_id": axis_id,
        "axis_name": axis["name"],
        "post_text": post_text,
        "kpi": kpi,
    }
