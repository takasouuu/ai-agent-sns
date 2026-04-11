# investment_agent — 投資系X投稿 SNS エージェント

YouTube動画（岐阜暴威ライブ配信 / 楽待チャンネル株関連回）と
X/Twitter トレンドニュースを解析し、投資関連のX投稿案を自動生成します。

---

## ディレクトリ構成

```
investment_agent/
├── agent.py          # メインエントリポイント（CLI）
├── config.py         # 設定・定数・チャンネル情報
├── post_builder.py   # 投稿文生成ロジック（5訴求軸）
├── news_fetcher.py   # X/Twitter API ニュース取得
├── .env.example      # API キー設定サンプル
└── README.md         # このファイル
```

---

## セットアップ

```bash
# 1. 依存パッケージをインストール
pip install yt-dlp

# ffmpeg が未インストールの場合（动画スクショに必要）
brew install ffmpeg   # macOS

# 2. 環境変数を設定（ニュースモードに必要）
cp investment_agent/.env.example investment_agent/.env
# .env を編集して TWITTER_BEARER_TOKEN 等を設定

# 3. .env を読み込む（毎回 or .bashrc/.zshrc に追記）
set -a; source investment_agent/.env; set +a
```

---

## 使い方

### a) 岐阜暴威 ライブ配信動画から投稿案生成

```bash
# スクショあり（動画をダウンロード）
python -m investment_agent.agent video \
  --url "https://www.youtube.com/watch?v=XXXXXXXXX" \
  --source gifuboui

# 高速モード（投稿文のみ / スクショなし）
python -m investment_agent.agent video \
  --url "https://www.youtube.com/watch?v=XXXXXXXXX" \
  --source gifuboui --fast
```

### b) 楽待チャンネル 株関連回から投稿案生成

```bash
python -m investment_agent.agent video \
  --url "https://www.youtube.com/watch?v=XXXXXXXXX" \
  --source rakumachi_stock
```

### c) X/Twitter 投資トレンド速報から投稿案生成

```bash
# APIキーなしでモックデータ確認
python -m investment_agent.agent news --dry-run

# 本番（.env に TWITTER_BEARER_TOKEN が設定済みであること）
python -m investment_agent.agent news
```

---

## 出力構成

```
output/
└── YYYY-MM-DD_動画タイトル_VideoID/
    ├── video_info.txt          # 動画情報・根拠説明
    ├── 1/
    │   ├── post.txt            # X投稿本文（--- 上がそのまま貼り付け可能）
    │   ├── screenshots_meta.txt
    │   ├── screenshot1.png
    │   ├── screenshot2.png
    │   ├── screenshot3.png
    │   └── screenshot4.png
    ├── 2/
    ...
    └── 5/
```

### post.txt フォーマット

```
（冒頭フック1行）
（要点2〜3個）
（CTA1行）
#投資 #株式投資 #訴求軸別ハッシュタグ
---
- 訴求軸:
- 想定ターゲット:
- CTA意図:
- 使用ハッシュタグ:
- 事実根拠（字幕/ニュース要約）:
- KPI自己評価（フック/保存/共感/会話/遷移）:
```

---

## 5訴求軸

| # | 軸名 | CTA | 主なKPI |
|---|------|-----|---------|
| 1 | 投資戦略・手法の具体性 | 保存 | フック A・保存 A |
| 2 | リスク管理・メンタル | 引用・感想募集 | 共感 A・会話 A |
| 3 | 銘柄・相場環境分析 | 動画視聴遷移 | 遷移 A・共感 A |
| 4 | 投資家の思考・哲学 | 保存 | 保存 A・会話 A |
| 5 | 速報・ニュース活用 | 引用・感想募集 | フック A・会話 A |

---

## ニュース取得について（X/Twitter API）

- **Free Tier** で利用可能な `/2/tweets/search/recent` を使用
- `TWITTER_BEARER_TOKEN` のみ設定すれば動作します
- API キー未設定または `--dry-run` 時はモックデータで動作します
- 取得キーワードは `config.py` の `NEWS_QUERY_KEYWORDS` で変更可能

---

## チャンネル追加方法

`config.py` の `CHANNELS` 辞書に新しいエントリを追加してください。

```python
"new_channel_key": {
    "name": "チャンネル表示名",
    "url": "https://www.youtube.com/@...",
    "label": "コンテンツ種別",
    "keywords": ["キーワード1", "キーワード2", ...],
    "hashtag_fixed": ["#固定タグ1", "#固定タグ2"],
},
```

---

## 注意事項

- 投稿文は**誇張表現・断定的な投資勧誘を含まない**よう設計されています
- 「必ず儲かる」等の断定表現は生成しません
- 登場する数値・発言は字幕・ニュース原文に基づきます
- 本ツールで生成した投稿を実際に投稿する前に必ず内容をご確認ください
