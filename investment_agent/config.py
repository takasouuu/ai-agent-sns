"""
investment_agent/config.py
設定・定数・チャンネル情報の一元管理
"""

from __future__ import annotations

import os
from pathlib import Path

# ─────────────────────────────────────────────
# パス
# ─────────────────────────────────────────────
ROOT = Path(__file__).resolve().parents[1]
WORK = Path(__file__).resolve().parent
TMP  = ROOT / "tmp_investment"
OUT_ROOT = ROOT / "output"

# ─────────────────────────────────────────────
# 対象チャンネル設定
# ─────────────────────────────────────────────
CHANNELS = {
    "gifuboui": {
        "name": "岐阜暴威",
        "url": "https://www.youtube.com/@岐阜暴威",
        "label": "投資系ライブ配信",
        "keywords": ["デイトレ", "スキャルピング", "損切り", "チャート", "板読み",
                     "エントリー", "利確", "相場", "ストップ高", "決算"],
        "hashtag_fixed": ["#岐阜暴威", "#デイトレ"],
    },
    "rakumachi_stock": {
        "name": "楽待【不動産投資専門チャンネル】",
        "url": "https://www.youtube.com/@rakumachi",
        "label": "株関連回",
        "keywords": ["配当", "割安", "PER", "PBR", "成長株", "決算", "銘柄",
                     "セクター", "高配当", "優待", "分散"],
        "hashtag_fixed": ["#楽待", "#高配当株"],
    },
}

# ─────────────────────────────────────────────
# 5訴求軸（固定）
# ─────────────────────────────────────────────
AXES = [
    {
        "id": 1,
        "name": "投資戦略・手法の具体性",
        "target": "具体的な売買ルールを知りたいトレーダー・投資初中級者",
        "cta": "保存",
        "hashtag_var": "#投資戦略",
        "angle": "具体的なエントリー/エグジット条件・売買ルール",
    },
    {
        "id": 2,
        "name": "リスク管理・メンタル",
        "target": "損切りや感情コントロールに悩む投資家",
        "cta": "引用・感想募集",
        "hashtag_var": "#リスク管理",
        "angle": "損切り基準・ポジションサイズ・メンタル管理",
    },
    {
        "id": 3,
        "name": "銘柄・相場環境分析",
        "target": "銘柄選定・市場動向に関心があるスイング・長期投資家",
        "cta": "動画視聴遷移",
        "hashtag_var": "#銘柄分析",
        "angle": "注目銘柄・セクター・マクロ環境の読み解き方",
    },
    {
        "id": 4,
        "name": "投資家の思考・哲学",
        "target": "投資観や軸を磨きたい20〜40代の投資家",
        "cta": "保存",
        "hashtag_var": "#投資哲学",
        "angle": "長期視点・資産形成の考え方・失敗から得た教訓",
    },
    {
        "id": 5,
        "name": "速報・ニュース活用",
        "target": "市場ニュースをいち早く投資に活かしたい全投資家",
        "cta": "引用・感想募集",
        "hashtag_var": "#投資情報",
        "angle": "ホットニュースの背景と投資への示唆",
    },
]

# ─────────────────────────────────────────────
# Twitter/X API 設定（.env から読み込み）
# ─────────────────────────────────────────────
TWITTER_BEARER_TOKEN = os.environ.get("TWITTER_BEARER_TOKEN", "")
TWITTER_API_KEY      = os.environ.get("TWITTER_API_KEY", "")
TWITTER_API_SECRET   = os.environ.get("TWITTER_API_SECRET", "")
TWITTER_ACCESS_TOKEN = os.environ.get("TWITTER_ACCESS_TOKEN", "")
TWITTER_ACCESS_SECRET= os.environ.get("TWITTER_ACCESS_SECRET", "")

# ニュース検索キーワード（X検索クエリ用）
NEWS_QUERY_KEYWORDS = [
    "日経平均 OR 日経225 OR 東証",
    "米国株 OR S&P500 OR NASDAQ",
    "NISA OR iDeCo OR 新NISA",
    "決算 OR 上方修正 OR 下方修正",
    "日銀 OR 利上げ OR 利下げ",
]
NEWS_MAX_RESULTS = 20          # 1キーワードあたり最大取得件数
NEWS_HOURS_BACK  = 6           # 過去何時間以内のツイートを対象にするか

# ─────────────────────────────────────────────
# ffmpeg / yt-dlp
# ─────────────────────────────────────────────
SHOTS_PER_SET  = 4             # 1セットあたりのスクショ枚数
NUM_SETS       = 5             # 訴求軸ごとに1セット
YT_DLP_OPTS    = [             # yt-dlp に渡す共通オプション
    "--write-info-json",
    "--write-subs",
    "--sub-langs", "ja",
    "--skip-download",         # fast_mode=True のとき動画本体は不要
]
YT_DLP_VIDEO_OPTS = [          # 動画本体も取得するとき
    "--write-info-json",
    "--write-subs",
    "--sub-langs", "ja",
    "-f", "bestvideo[ext=webm]+bestaudio[ext=webm]/best[ext=webm]/best",
]
