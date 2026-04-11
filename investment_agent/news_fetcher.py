"""
investment_agent/news_fetcher.py
X（旧Twitter）API v2 を使って投資関連ホットニュースを早期検知するモジュール

必要な環境変数（.env に設定）:
  TWITTER_BEARER_TOKEN  : X API v2 Bearer Token（App-only）
"""

from __future__ import annotations

import json
import logging
import re
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from typing import Any

from .config import (
    NEWS_HOURS_BACK,
    NEWS_MAX_RESULTS,
    NEWS_QUERY_KEYWORDS,
    TWITTER_BEARER_TOKEN,
)

logger = logging.getLogger(__name__)

X_SEARCH_URL = "https://api.twitter.com/2/tweets/search/recent"


# ──────────────────────────────────────────────────────────────
# メイン関数
# ──────────────────────────────────────────────────────────────
def fetch_investment_news(
    hours_back: int = NEWS_HOURS_BACK,
    max_results_per_query: int = NEWS_MAX_RESULTS,
    dry_run: bool = False,
) -> list[dict[str, Any]]:
    """
    各クエリキーワードで最近のツイートを検索し、トピックにまとめて返す。

    Parameters
    ----------
    hours_back             : 過去何時間分を対象にするか
    max_results_per_query  : 1クエリあたりの最大取得件数（API制限: 10〜100）
    dry_run                : True のときはモックデータを返す（APIキー不要）

    Returns
    -------
    list of dict
        {topic, summary, tweets:[{text, created_at, like_count}], query}
    """
    if dry_run or not TWITTER_BEARER_TOKEN:
        logger.warning("dry_run mode: X API を呼び出さずにモックデータを使用します")
        return _mock_news_items()

    results = []
    since_dt = (datetime.now(timezone.utc) - timedelta(hours=hours_back)).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )

    for query_kw in NEWS_QUERY_KEYWORDS:
        try:
            tweets = _search_tweets(query_kw, since_dt, max_results_per_query)
            if not tweets:
                continue
            topic   = _extract_topic(query_kw, tweets)
            summary = _summarize_tweets(tweets)
            results.append(
                {
                    "topic": topic,
                    "summary": summary,
                    "tweets": tweets,
                    "query": query_kw,
                }
            )
            logger.info("取得: %s (%d件)", topic, len(tweets))
        except Exception as exc:
            logger.error("クエリ [%s] 取得失敗: %s", query_kw, exc)

    # いいね合計数でランキング（バズり度順）
    results.sort(key=lambda x: sum(t.get("like_count", 0) for t in x["tweets"]), reverse=True)
    return results[:5]  # 上位5トピックのみ返す


# ──────────────────────────────────────────────────────────────
# X API v2 呼び出し
# ──────────────────────────────────────────────────────────────
def _search_tweets(
    query_kw: str, since_dt: str, max_results: int
) -> list[dict[str, Any]]:
    """X API v2 recent search エンドポイントを呼んでツイートリストを返す"""
    # RT・スパムを除外し日本語に絞る
    full_query = f"({query_kw}) lang:ja -is:retweet -is:reply"

    params = {
        "query": full_query,
        "max_results": str(min(max(10, max_results), 100)),
        "start_time": since_dt,
        "tweet.fields": "created_at,public_metrics,text",
        "sort_order": "relevancy",
    }
    url = X_SEARCH_URL + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(
        url,
        headers={"Authorization": f"Bearer {TWITTER_BEARER_TOKEN}"},
    )

    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode())

    tweets = []
    for t in data.get("data", []):
        metrics = t.get("public_metrics", {})
        tweets.append(
            {
                "text":       t.get("text", ""),
                "created_at": t.get("created_at", ""),
                "like_count": metrics.get("like_count", 0),
                "rt_count":   metrics.get("retweet_count", 0),
            }
        )

    # いいね数降順でソート
    tweets.sort(key=lambda x: x["like_count"], reverse=True)
    return tweets


# ──────────────────────────────────────────────────────────────
# テキスト処理ユーティリティ
# ──────────────────────────────────────────────────────────────
def _extract_topic(query_kw: str, tweets: list[dict]) -> str:
    """クエリキーワードとツイート先頭から簡易トピック名を生成する"""
    # クエリを OR 分解し最初のキーワードを使う
    keywords = re.split(r"\s+OR\s+", query_kw)
    topic_kw = keywords[0].replace("(", "").replace(")", "").strip()

    # よく登場する固有名詞を補完
    top_text = tweets[0]["text"] if tweets else ""
    for word in ["日経", "S&P", "NISA", "日銀", "決算", "円安", "円高"]:
        if word in top_text and word not in topic_kw:
            topic_kw += f"・{word}"
            break

    return topic_kw


def _summarize_tweets(tweets: list[dict], top_n: int = 5) -> str:
    """上位 top_n ツイートを連結して要約文字列を返す（最大120字）"""
    parts = []
    for t in tweets[:top_n]:
        # URL・絵文字・ハッシュタグを除去
        text = re.sub(r"https?://\S+", "", t["text"])
        text = re.sub(r"[#＃@＠]\S+", "", text)
        text = re.sub(r"\s+", " ", text).strip()
        if text:
            parts.append(text[:30])
    return "／".join(parts)[:120]


# ──────────────────────────────────────────────────────────────
# モックデータ（dry_run / API キーなし時）
# ──────────────────────────────────────────────────────────────
def _mock_news_items() -> list[dict[str, Any]]:
    return [
        {
            "topic": "日経平均・相場動向",
            "summary": "日経平均が一時38,000円を超えた／米雇用統計を受けた動き",
            "tweets": [
                {"text": "日経平均が一時38,000円を超えました。今後の展開が注目されます。", "created_at": "", "like_count": 320, "rt_count": 80},
                {"text": "米雇用統計の結果を受けて日本株が反応。セクターローテーションに注目。", "created_at": "", "like_count": 210, "rt_count": 55},
            ],
            "query": "日経平均 OR 日経225 OR 東証",
        },
        {
            "topic": "米国株・S&P500",
            "summary": "S&P500が最高値更新／テック株中心に上昇",
            "tweets": [
                {"text": "S&P500が最高値を更新。テック株中心に買いが集まっています。", "created_at": "", "like_count": 450, "rt_count": 120},
            ],
            "query": "米国株 OR S&P500 OR NASDAQ",
        },
        {
            "topic": "新NISA活用術",
            "summary": "新NISA成長投資枠の活用法が話題に／インデックス vs 個別株の議論",
            "tweets": [
                {"text": "新NISAの成長投資枠でインデックスか個別株か迷っている人が多い印象。", "created_at": "", "like_count": 280, "rt_count": 70},
            ],
            "query": "NISA OR iDeCo OR 新NISA",
        },
        {
            "topic": "決算・上方修正",
            "summary": "3月期本決算シーズン到来／上方修正銘柄に注目",
            "tweets": [
                {"text": "3月決算シーズン本番。上方修正銘柄をスクリーニングするのが今のトレンド。", "created_at": "", "like_count": 195, "rt_count": 40},
            ],
            "query": "決算 OR 上方修正 OR 下方修正",
        },
        {
            "topic": "日銀・金利動向",
            "summary": "日銀の追加利上げ観測が再浮上／円高方向に振れる可能性",
            "tweets": [
                {"text": "日銀の追加利上げ観測が再び浮上。円高方向に振れると輸出株は要注意。", "created_at": "", "like_count": 370, "rt_count": 95},
            ],
            "query": "日銀 OR 利上げ OR 利下げ",
        },
    ]
