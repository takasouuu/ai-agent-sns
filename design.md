# 週次報告デザイン（システム開発プロジェクト / GitHub Copilot運用）

## 1. 目的
- Redmineのチケットデータを根拠に、開発プロジェクトの進捗と課題を週次で可視化する。
- マネージャー・開発メンバー・関係者が、同じ事実を見て次週の優先順位を決められる状態を作る。

## 2. 週次報告のゴール
- 進捗: 計画に対して何が完了し、何が未完了かを示す。
- 品質: バグ流入や再オープンなど品質劣化の兆候を示す。
- リスク: 遅延要因、ブロッカー、依存関係を示す。
- 次アクション: 次週の実行項目と担当を明確化する。

## 3. 入力データ（Redmine API）
- 対象期間: 直近7日（例: 2026-04-13 00:00:00 〜 2026-04-19 23:59:59）
- 取得元: Redmine REST API
- 主な取得対象:
  - チケット一覧（status, tracker, priority, assignee, due_date, done_ratio）
  - 期間内の更新履歴（status変更、担当変更、期限変更）
  - 作業時間（spent_time）

## 4. 最低限の集計指標（KPI）
- 完了件数: 期間内に完了（Closed/Resolved）したチケット数
- 新規起票件数: 期間内に新規作成されたチケット数
- 未完了件数: 期間末時点の未完了チケット数
- バグ件数: 期間内のバグ起票数とクローズ数
- 再オープン件数: Reopenedになった件数
- 期限超過件数: 期限を過ぎた未完了チケット数
- 工数実績: 期間内の実績工数（h）

## 5. Redmine API取得例
環境変数を設定して実行する。

```bash
export REDMINE_BASE_URL="https://your-redmine.example.com"
export REDMINE_API_KEY="your_api_key"
export PROJECT_ID="your_project"
export FROM_DATE="2026-04-13"
export TO_DATE="2026-04-19"
```

### 5.1 チケット一覧（必要項目のみ）
```bash
curl -s "$REDMINE_BASE_URL/issues.json?project_id=$PROJECT_ID&limit=100&status_id=*&updated_on=%3E%3D$FROM_DATE" \
  -H "X-Redmine-API-Key: $REDMINE_API_KEY" \
  -H "Content-Type: application/json" > tmp_analysis/redmine_issues.json
```

### 5.2 作業時間
```bash
curl -s "$REDMINE_BASE_URL/time_entries.json?project_id=$PROJECT_ID&from=$FROM_DATE&to=$TO_DATE&limit=100" \
  -H "X-Redmine-API-Key: $REDMINE_API_KEY" \
  -H "Content-Type: application/json" > tmp_analysis/redmine_time_entries.json
```

必要に応じてページング（offset）を追加する。

## 6. Copilotに渡すプロンプト（そのまま利用可）
以下をGitHub Copilot Chat（Agentモード）に貼り付ける。

あなたはシステム開発プロジェクトの週次報告アナリストです。
以下のRedmine API取得データを読み、週次報告を作成してください。

対象ファイル:
- tmp_analysis/redmine_issues.json
- tmp_analysis/redmine_time_entries.json

要件:
1. サマリー（3行）
2. 進捗サマリー（完了/新規/未完了、主要マイルストーンの達成状況）
3. 品質サマリー（バグ起票/解消、再オープン、重大インシデント有無）
4. リスクと課題（期限超過、依存関係、ブロッカー）
5. 次週アクション（最大3件、担当ロール付き）
6. 補足データ（主要チケットID一覧）

制約:
- 事実と解釈を分けて記述
- 断定的な原因決めつけをしない
- 数値は可能な限り明記し、根拠ファイルを示す

出力形式:
- Markdown
- 見出し順は要件どおり
- 箇条書き中心で簡潔に

## 7. 週次報告テンプレート
以下を weekly_report_YYYY-MM-DD.md として保存する。

# 週次報告（YYYY-MM-DD）

## 1. サマリー
- 
- 
- 

## 2. 進捗サマリー
- 完了件数: 
- 新規起票件数: 
- 未完了件数: 
- マイルストーン進捗: 

## 3. 品質サマリー
- バグ起票件数: 
- バグ解消件数: 
- 再オープン件数: 
- 重大インシデント: 

## 4. リスクと課題
- 期限超過チケット: 
- ブロッカー: 
- 依存関係の懸念: 

## 5. 次週アクション（優先順）
1. 内容:  / 担当:  / 期限: 
2. 内容:  / 担当:  / 期限: 
3. 内容:  / 担当:  / 期限: 

## 6. 補足データ
- 実績工数（h）: 
- 主要チケットID:
  - 
  - 
  - 

## 7. 運用ルール
- 毎週末に1回作成する。
- 根拠データはRedmine API取得結果のみを使用する。
- 次週アクションは最大3件までに制限する。
- 報告は5分以内で読める分量（簡潔）にする。

## 8. 品質チェック（提出前）
- KPI（完了/新規/未完了/バグ/工数）がすべて埋まっている。
- リスクに対して対応アクションが定義されている。
- 主要チケットIDが追跡可能な形で記載されている。
- 事実と解釈が混在していない。
