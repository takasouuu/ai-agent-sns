# Skill: redmine-weekly-report

## Purpose
Redmine APIを根拠に、システム開発プロジェクトの週次報告を一貫した品質で作成する。

## Use this skill when
- 週次報告を作るとき
- 進捗/品質/リスクを定量で示すとき
- 次週アクションを優先順で決めるとき

## Canonical Data Source
- Redmine REST API
- issues.json（チケット）
- time_entries.json（工数）

## Required KPI
1. 完了件数（Closed/Resolved）
2. 新規起票件数
3. 未完了件数
4. バグ起票件数 / 解消件数
5. 再オープン件数
6. 期限超過件数
7. 実績工数（h）

## Writing Guardrails
- 事実と解釈を分ける
- 数値には根拠ファイルを持たせる
- 断定的な原因決めつけをしない
- 次週アクションは最大3件

## Report Structure
1. サマリー
2. 進捗サマリー
3. 品質サマリー
4. リスクと課題
5. 次週アクション
6. 補足データ
