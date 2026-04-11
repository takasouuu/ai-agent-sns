# SNS-X Business ワークフロー

## 概要
しごとリーチのYouTube動画をX（旧Twitter）投稿に変換するマルチエージェント自動化パイプライン。

```
[STEP 1] sns-x-research-agent
     ↓ 候補動画リスト（candidate_videos.md）
[USER DECISION 1] どの動画を投稿化するか選択
     ↓ 選択された video_id
[STEP 2] sns-x-editorial-agent
     ↓ outputs/{date}_{title}/{1-5}/ （5セット）
[STEP 3] sns-x-review-agent
     ├─ NG → sns-x-editorial-agent に差し戻し（最大5回）
     └─ OK ↓
[USER DECISION 2] どの投稿案（1〜5）を採用するか選択
     ↓
[STEP 4] 投稿履歴に video_id を記録（posted_history.json）
```

---

## STEP 1: リサーチエージェント（sns-x-research-agent）

**担当**: [sns-x-research-agent.md](../agents/sns-x-research-agent.md)

**処理内容**:
1. しごとリーチチャンネルの最新・人気動画を取得（yt-dlp / RSS等）
2. `posted_history.json` と照合し投稿済みを除外
3. 指定基準でスコアリングし上位5〜10件を候補として出力
4. `tmp_analysis/candidate_videos.md` に保存

**出力ファイル**: `tmp_analysis/candidate_videos.md`

---

## STEP 2: 編集エージェント（sns-x-editorial-agent）

**担当**: [sns-x-editorial-agent.md](../agents/sns-x-editorial-agent.md)

**入力**: `video_id`（USER DECISION 1 で決定）

**処理内容**:
1. yt-dlp で動画・字幕・コメント取得
2. 字幕解析（重要発言・制度・価値観を抽出）
3. 5訴求軸にマッピング
4. 各軸ごとにスクリーンショット候補を選定（4〜5枚）
5. 品質チェック後に画像を確定
6. post.txt・screenshots_meta.txt・video_info.txt を生成

**出力ディレクトリ**: `outputs/YYYY-MM-DD_タイトル_VideoID/{1〜5}/`

**差し戻し時**: sns-x-review-agent から指摘内容を受け取り修正。最大5回まで対応。

---

## STEP 3: レビューエージェント（sns-x-review-agent）

**担当**: [sns-x-review-agent.md](../agents/sns-x-review-agent.md)

**入力**: STEP 2 の出力ディレクトリ

**処理内容**:
1. 投稿文と画像の品質チェック（全チェックリスト適用）
2. NG の場合: 差し戻し理由を `review_feedback.md` に記録し STEP 2 に差し戻し
3. OK の場合: `review_passed.md` を生成してユーザーに通知

**ループ上限**: 最大5回。5回を超えてもNG の場合はユーザーに手動確認を依頼。

---

## USER DECISION 2: 投稿案の採用

ユーザーが `outputs/YYYY-MM-DD_xxx/{1〜5}/post.txt` を確認し1案を選択。

---

## STEP 4: 投稿履歴更新

選択確定後、`data/posted_history.json` に以下を追記:
```json
{
  "video_id": "XXXXXXXXXXX",
  "title": "動画タイトル",
  "posted_date": "YYYY-MM-DD",
  "used_set": 3,
  "output_dir": "outputs/2026-04-12_xxx"
}
```

---

## 推奨追加エージェント（将来的な拡張案）

| エージェント | 役割 | 優先度 |
|---|---|---|
| sns-x-scheduler-agent | 最適投稿時間帯の提案（曜日・時間帯分析） | Medium |
| sns-x-analytics-agent | X投稿のエンゲージメント追跡・KPI集計 | Medium |
| sns-x-thumbnail-agent | Gemini APIでサムネ/補足画像を自動生成 | Low |
| sns-x-hashtag-agent | X検索トレンドに基づくハッシュタグ最適化 | Low |

---

## ファイル構成

```
.github/
  agents/
    sns-x-research-agent.md     # STEP 1
    sns-x-editorial-agent.md    # STEP 2
    sns-x-review-agent.md       # STEP 3
    sns-x-business-agent.md     # オーケストレーター（ブランド基準・全体管理）
  workflows/
    sns-x-business-workflow.md  # このファイル（全体設計）
data/
  posted_history.json           # 投稿済み動画の記録
tmp_analysis/
  candidate_videos.md           # リサーチ結果の候補リスト（都度上書き）
outputs/
  YYYY-MM-DD_タイトル/
    1/ ... 5/                   # 各セット
```
