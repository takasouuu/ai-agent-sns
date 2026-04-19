# Skill: redmine-weekly-report

## Purpose
Redmine APIを根拠に、システム開発プロジェクトの週次報告を一貫した品質で作成する。

## Use this skill when
- 週次報告を作るとき
- 進捗/品質/リスクを定量で示すとき
- 次週アクションを優先順で決めるとき
- mock UIを高再現で静的HTML化するとき

## Canonical Data Source
- Redmine REST API
- 複数のRedmine URL
- issues.json（チケット）
- time_entries.json（工数）

## Managed Areas
1. タスク管理
2. 内部課題管理
3. 外部課題管理
4. リスク管理
5. 不具合管理
6. 変更管理

## Required KPI
1. 完了件数（Closed/Resolved）
2. 新規起票件数
3. 未完了件数
4. バグ起票件数 / 解消件数
5. 再オープン件数
6. 期限超過件数
7. 実績工数（h）
8. SPI（EV/PV）
9. CPI（EV/AC）

## Writing Guardrails
- 事実と解釈を分ける
- 数値には根拠ファイルを持たせる
- 断定的な原因決めつけをしない
- 次週アクションは最大3件

## Report Structure
1. サマリー
2. 領域別サマリー
3. 進捗サマリー
4. 品質サマリー
5. リスクと課題
6. 次週アクション
7. 補足データ

## UI Reproducibility Contract
- UIの正本は outputs/weekly/mock/index.html と outputs/weekly/mock/style.css。
- 生成時は必ずテンプレート複製を起点にする（新規HTML骨組みの生成禁止）。
- DOM構造、主要クラス名、セクション順序は固定する。
- 変更可能なのは文字列値、数値、表行データ、タブ内テキストのみ。
- 変更不可: 主要ラッパー（page-shell/report-header/kpi-grid/domain-grid/test-group-details/insight-grid/detail-grid/member-table）の追加削除。
- 禁止表示: Blocker / External Dependency / Technical Debt / Decision / Escalation。

## Required DOM Signature (must exist)
- .page-shell
- header.report-header.card
- section.kpi-grid
- section.card.section-card .core-domain-grid
- details.test-group-details
- section.insight-grid
- details.overdue-details
- article.qualitative-panel
- table.member-table

## Mapping Rule (Markdown to Mock UI)
- weekly_report の KPI -> .kpi-grid 8カード
- 領域別サマリー -> .core-domain-grid 5カード
- テストグループ -> details.test-group-details 内3パネル
- 進捗/コスト/リスク -> .insight-grid の3パネル
- 次週アクション -> .action-panel の ol.action-list
- 期日超過 -> .overdue-details > .ticket-table
- 定性評価 -> .qualitative-panel
- 個人別サマリー -> .member-table
- dev_progress_meeting -> 単一HTMLの会議タブ

## Self Check
1. テンプレートを複製起点にしたか確認。
2. Required DOM Signature の全要素が存在するか確認。
3. セクション順序が mock と一致するか確認。
4. validate_weekly_output.py を実行しPASSを確認。
