# ai-agent-sns

しごとリーチの YouTube 動画を X（旧Twitter）投稿に変換するマルチエージェント自動化プロジェクト。

---

## エージェント構成

| エージェント    | ファイル                    | 役割              |
| --------- | ----------------------- | --------------- |
| オーケストレーター | `sns-x-business-agent`  | 全体統括・ワークフロー進行   |
| リサーチ      | `sns-x-research-agent`  | 投稿候補動画の選定       |
| 編集        | `sns-x-editorial-agent` | 投稿文・スクリーンショット生成 |
| レビュー      | `sns-x-review-agent`    | 品質チェック・差し戻し判定   |

詳細: [.github/workflows/sns-x-business-workflow.md](.github/workflows/sns-x-business-workflow.md)

---

## ワークフロー実行プロンプト例

GitHub Copilot Chat を **Agent モード** にして、以下のプロンプトをコピー&ペーストしてください。

### 1. ワークフロー全体を最初から開始する

```
@sns-x-business-agent 今日の投稿コンテンツを作りたい。
ワークフローを最初から実行してください。
```

---

### 2. リサーチだけ実行する（候補動画リストの更新）

```
@sns-x-researc-agent しごとリーチの最新・人気動画を調査して、
候補リストを tmp_analysis/candidate_videos.md に出力してください。
```

---

### 3. 動画を指定して編集を開始する

候補リストまたは任意の URL を直接指定するパターン:

```
@sns-x-editorial-agent 次の動画で投稿5セットを作成してください。
video_id: ZQidQOAZfog
```

もしくは URL 指定:

```
@sns-x-editorial-agent 次のURLの動画で投稿5セットを作成してください。
https://www.youtube.com/watch?v=ZQidQOAZfog
```

---

### 4. 生成済み出力のレビューを依頼する

```
@sns-x-review-agent 以下のディレクトリの投稿5セットをレビューしてください。
output/2026-04-11_タイトル_VideoID/
```

---

### 5. レビューNGで差し戻し後に再生成する（編集エージェントへ）

```
@sns-x-editorial-agent レビューフィードバックに基づき修正してください。
video_id: ZQidQOAZfog
フィードバックファイル: output/2026-04-11_タイトル_VideoID/review_feedback.md
```

---

### 6. 投稿案を確定して履歴に記録する

ユーザーがセット番号を選んだ後、オーケストレーターに記録を依頼:

```
@sns-x-business-agent セット3を採用します。
video_id: ZQidQOAZfog
output_dir: output/2026-04-11_タイトル_VideoID/
posted_history.json に記録してください。
```

---

### 7. 投稿済み履歴を確認する

```
@sns-x-business-agent これまでに投稿した動画の一覧を表示してください。
data/posted_history.json を参照してください。
```

---

## Redmine週次報告ワークフロー実行プロンプト例

GitHub Copilot Chat を **Agent モード** にして、以下のプロンプトを利用してください。

### 1. 週次報告ワークフローを一括実行する

```
@redmine-weekly-workflow Redmine APIを使って週次報告を作成してください。
対象期間は 2026-04-13 から 2026-04-19 です。
RedmineのURLはエージェント設定ファイル定義を参照してください。
```

---

### 2. Redmineデータ収集のみ実行する

```
@redmine-weekly-data-agent Redmine APIから週次報告データを取得してください。
FROM_DATE: 2026-04-13
TO_DATE: 2026-04-19
領域別issueファイルと工数ファイルを tmp_analysis 配下に保存してください。
RedmineのURLはエージェント設定ファイル定義を参照してください。
```

---

### 3. 収集済みデータから週次報告を作成する

```
@redmine-weekly-analysis-agent 領域別の Redmine issue ファイルと
工数ファイルを使って週次報告を作成してください。
タスク管理、内部課題管理、外部課題管理、リスク管理、不具合管理、変更管理の
6領域ごとのサマリーも含めてください。
outputs/weekly/weekly_report_2026-04-19.md に出力してください。
```

---

### 4. 週次報告ドラフトをレビューする

```
@redmine-weekly-review-agent outputs/weekly/weekly_report_2026-04-19.md をレビューしてください。
KPI欠落、根拠不足、曖昧表現を確認し、
OKなら outputs/weekly/review_passed.md、NGなら outputs/weekly/review_feedback.md を作成してください。
```

---

## ディレクトリ構成

```
.github/
  agents/
    sns-x-business-agent.md      # オーケストレーター
    sns-x-research-agent.md      # リサーチ
    sns-x-editorial-agent.md     # 編集
    sns-x-review-agent.md        # レビュー
    redmine-weekly-workflow.md   # Redmine週次報告ワークフロー
    redmine-weekly-data-agent.md # Redmineデータ収集
    redmine-weekly-analysis-agent.md # 週次報告作成
    redmine-weekly-review-agent.md # 週次報告レビュー
  workflows/
    sns-x-business-workflow.md   # ワークフロー設計書
  instructions/
    sns-x-business.instructions.md
  prompts/
    sns-x-business-post.prompt.md
    sns-x-business-icon-gemini.prompt.md
  skills/
    sns-x-business-brand/SKILL.md
    redmine-weekly-report/SKILL.md
  copilot-instructions.md        # ブランド定数（全エージェント共通）

data/
  posted_history.json            # 投稿済み動画の重複防止用履歴

tmp_analysis/
  candidate_videos.md            # リサーチ結果（都度上書き）
  *.info.json / *.ja.vtt         # yt-dlp 作業ファイル
  redmine_*_issues.json          # Redmine領域別チケット
  redmine_*_time_entries.json    # Redmine領域別工数

output/
  YYYY-MM-DD_タイトル_VideoID/
    1/ ～ 5/                     # 各セット（post.txt, screenshot*.png 等）

outputs/
  weekly/
    weekly_report_YYYY-MM-DD.md  # Redmine週次報告
    review_passed.md
    review_feedback.md
```

---

## ブランド情報

- **アカウント名**: 10秒キャリア解像度
- **ユーザー名**: @10sec_careerlab
- **コンセプト**: 1投稿10秒で学べる。情熱・実務・文化を短く深く。
- **対象**: 転職検討者・副業検討者・キャリアアップ志向層
- lll

画像コンセプト詳細: [.github/prompts/sns-x-business-icon-gemini.prompt.md](.github/prompts/sns-x-business-icon-gemini.prompt.md)
