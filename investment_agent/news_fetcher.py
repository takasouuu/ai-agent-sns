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
    NEWS_RSS_FEEDS,
    NOTE_RSS_FEEDS,
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


# ──────────────────────────────────────────────────────────────
# RSS ニュースフィード取得
# ──────────────────────────────────────────────────────────────
def fetch_rss_news(
    hours_back: int = NEWS_HOURS_BACK,
) -> list[dict[str, Any]]:
    """
    RSS フィードから投資関連ニュース記事を取得する。

    Parameters
    ----------
    hours_back : 過去何時間分を対象にするか

    Returns
    -------
    list of dict
        {source, title, summary, published_at, url}
    """
    try:
        import feedparser  # type: ignore
    except ImportError:
        logger.warning("feedparser not installed. Run: pip install feedparser")
        return []

    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours_back)
    articles: list[dict[str, Any]] = []

    all_feeds = list(NEWS_RSS_FEEDS) + [(f"note({i+1})", url) for i, url in enumerate(NOTE_RSS_FEEDS)]

    for source, url in all_feeds:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                pub = getattr(entry, "published_parsed", None)
                if pub:
                    pub_dt = datetime(*pub[:6], tzinfo=timezone.utc)
                    if pub_dt < cutoff:
                        continue
                title   = entry.get("title", "").strip()
                summary = re.sub(r"<[^>]+>", "", entry.get("summary", ""))[:200].strip()
                articles.append(
                    {
                        "source":       source,
                        "title":        title,
                        "summary":      summary,
                        "published_at": pub_dt.strftime("%Y-%m-%d %H:%M") if pub else "",
                        "url":          entry.get("link", ""),
                        "engagement":   0,  # RSS は engagement 不明
                    }
                )
            logger.info("RSS [%s]: %d件取得", source, len(articles))
        except Exception as exc:
            logger.error("RSS [%s] 取得失敗: %s", source, exc)

    return articles


# ──────────────────────────────────────────────────────────────
# トピック集約 + スコアリング
# ──────────────────────────────────────────────────────────────
_CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "決算":         ["決算", "上方修正", "下方修正", "増配", "配当", "四半期"],
    "要人発言":     ["日銀", "植田", "FRB", "パウエル", "財務大臣", "国債", "利上げ", "利下げ", "金融政策"],
    "IPO/CA":       ["IPO", "新規上場", "MBO", "TOB", "M&A", "増資", "自社株買い"],
    "銘柄急変動":   ["ストップ高", "ストップ安", "急騰", "急落", "大暴落", "最高値更新"],
    "テクニカル":   ["ゴールデンクロス", "デッドクロス", "移動平均", "チャート", "テクニカル", "支持線", "抵抗線"],
    "マクロ":       ["CPI", "GDP", "雇用統計", "インフレ", "円安", "円高", "USDJPY", "為替"],
    "銘柄分析":     ["銘柄", "セクター", "PER", "PBR", "ROE", "高配当", "成長株"],
}


def _classify_category(text: str) -> str:
    for cat, kws in _CATEGORY_KEYWORDS.items():
        if any(kw in text for kw in kws):
            return cat
    return "その他"


def score_topic(
    topic: dict[str, Any],
    now: datetime | None = None,
) -> int:
    """
    トピックをスコアリングする（0〜100点）。

    指標             配点
    鮮度             25
    エンゲージメント  20
    市場インパクト    20
    トピック多様性    15
    投稿文可能性      10
    コーポレートアクション 10
    """
    if now is None:
        now = datetime.now(timezone.utc)

    score = 0

    # 鮮度 (25点)
    pub_str = topic.get("published_at", "")
    if pub_str:
        try:
            pub_dt = datetime.strptime(pub_str, "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)
            hours_ago = (now - pub_dt).total_seconds() / 3600
            score += 25 if hours_ago <= 6 else 20 if hours_ago <= 12 else 14 if hours_ago <= 24 else 5
        except ValueError:
            pass

    # エンゲージメント (20点)
    eng = topic.get("engagement", 0)
    score += 20 if eng >= 1000 else 15 if eng >= 500 else 10 if eng >= 100 else 5 if eng >= 10 else 0

    # 市場インパクト推定 (20点) — 指数・大型銘柄を優先
    title = topic.get("title", "") + topic.get("summary", "")
    if any(w in title for w in ["日経", "S&P", "NASDAQ", "日銀", "FRB", "FOMC"]):
        score += 20
    elif any(w in title for w in ["決算", "銘柄", "セクター"]):
        score += 12
    else:
        score += 5

    # トピック多様性 (15点) — sources 数
    sources = topic.get("sources", [])
    score += 15 if len(sources) >= 3 else 10 if len(sources) >= 2 else 5

    # 投稿文可能性 (10点) — 数値データあり
    if re.search(r"\d+[%円兆億万ドル.+\-]+", title):
        score += 10
    else:
        score += 5

    # コーポレートアクション (10点)
    cat = topic.get("category", "")
    if cat == "IPO/CA":
        score += 10
    elif cat == "決算":
        score += 8

    return min(score, 100)


def aggregate_and_score_topics(
    x_items:  list[dict[str, Any]],
    rss_items: list[dict[str, Any]],
    hours_back: int = NEWS_HOURS_BACK,
) -> list[dict[str, Any]]:
    """
    X ツイートと RSS 記事を集約し、重複排除後にスコアリングして返す。

    Returns
    -------
    上位10件のトピックリスト（score 降順）
    """
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(hours=hours_back)

    # X アイテムを topic 形式に変換
    topics: list[dict[str, Any]] = []
    for item in x_items:
        title = item.get("topic", item.get("summary", ""))[:60]
        cat   = _classify_category(title + item.get("summary", ""))
        tweets = item.get("tweets", [])
        engagement = sum(t.get("like_count", 0) + t.get("rt_count", 0) for t in tweets)
        pub_str = tweets[0].get("created_at", "") if tweets else ""
        if pub_str:
            try:
                pub_str = datetime.strptime(pub_str[:16], "%Y-%m-%dT%H:%M").strftime("%Y-%m-%d %H:%M")
            except ValueError:
                pub_str = now.strftime("%Y-%m-%d %H:%M")
        else:
            pub_str = now.strftime("%Y-%m-%d %H:%M")

        topics.append(
            {
                "topic_id":        f"{now.strftime('%Y%m%d')}_{title[:12]}",
                "title":           title,
                "category":        cat,
                "sources":         ["X"],
                "engagement":      engagement,
                "published_at":    pub_str,
                "key_facts":       [item.get("summary", "")[:100]],
                "related_tickers": [],
            }
        )

    # RSS アイテムを topic 形式に変換
    for art in rss_items:
        title = art.get("title", "")[:60]
        cat   = _classify_category(title + art.get("summary", ""))
        # 同一事象のトピックがすでにあれば sources にマージ
        merged = False
        for t in topics:
            # タイトルの類似度: 3文字以上の共通部分があれば同一扱い
            common_words = set(re.findall(r"[\u4e00-\u9fff]{2,}", t["title"])) & \
                           set(re.findall(r"[\u4e00-\u9fff]{2,}", title))
            if len(common_words) >= 2:
                t["sources"] = list(set(t["sources"] + [art["source"]]))
                t["key_facts"].append(art.get("summary", "")[:100])
                merged = True
                break
        if not merged:
            topics.append(
                {
                    "topic_id":        f"{now.strftime('%Y%m%d')}_{title[:12]}",
                    "title":           title,
                    "category":        cat,
                    "sources":         [art["source"]],
                    "engagement":      art.get("engagement", 0),
                    "published_at":    art.get("published_at", now.strftime("%Y-%m-%d %H:%M")),
                    "key_facts":       [art.get("summary", "")[:100]],
                    "related_tickers": [],
                }
            )

    # スコアリング
    for t in topics:
        t["score"] = score_topic(t, now=now)

    # スコア降順でソート → 上位10件
    topics.sort(key=lambda x: x["score"], reverse=True)
    return topics[:10]


def fetch_all_investment_news(
    hours_back: int = NEWS_HOURS_BACK,
    dry_run: bool = False,
) -> list[dict[str, Any]]:
    """
    X + RSS + note の全ソースから投資ニュースを取得し、集約・スコアリングして返す。

    Parameters
    ----------
    hours_back : 過去何時間分を対象にするか（デフォルト24h）
    dry_run    : True のときはモックデータを使用（APIキー不要）

    Returns
    -------
    上位10件のトピックリスト
    """
    # X API 取得
    x_items = fetch_investment_news(hours_back=hours_back, dry_run=dry_run)

    # RSS 取得
    rss_items = fetch_rss_news(hours_back=hours_back)

    # 集約・スコアリング
    return aggregate_and_score_topics(x_items, rss_items, hours_back=hours_back)
