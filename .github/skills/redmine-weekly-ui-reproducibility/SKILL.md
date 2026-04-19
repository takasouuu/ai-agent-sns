# Skill: redmine-weekly-ui-reproducibility

## Purpose
outputs/weekly/mock/index.html のUIを毎週のレポート生成で高再現に維持する。

## Use this skill when
- 週次報告HTML/CSSを生成・更新するとき
- テンプレート準拠のままデータ差し替えを行うとき
- レビューでUI差分の混入を防ぎたいとき

## Canonical Template
- outputs/weekly/mock/index.html
- outputs/weekly/mock/style.css

## Golden Rules
1. 生成は必ずテンプレート複製起点。
2. DOM構造・主要クラス名・セクション順序を保持。
3. 変更はテキスト/数値/表行に限定。
4. 単一HTMLタブ化時も週次報告側のDOM順序は保持。

## Frozen Selectors
- .page-shell
- .report-header
- .kpi-grid
- .core-domain-grid
- .test-group-details
- .insight-grid
- .overdue-details
- .qualitative-panel
- .member-table

## Section Order Contract
1. Header
2. KPI Summary Row
3. Domain Summary Grid
4. Test Group
5. Progress / Cost / Risk / Next Actions
6. Overdue / Qualitative
7. Member Table

## Allowed Additions
- タブ切替用: tab-switcher / tab-btn / tab-panel
- アクセシビリティ属性: aria-label, role, data-* 属性
- 追加パネル（Milestone/Release, Scope Change, Team Capacity, Weekly Trend）
  ただし既存セクション順序と主要DOMを壊さないこと

## Forbidden Changes
- セクション削除/並べ替え
- major class rename
- KPIカード基本構造変更
- 禁止パネルの表示

## Verification Checklist
1. validate_weekly_output.py が PASS。
2. Frozen Selectors が全件存在。
3. Test Group と Overdue が details 要素で展開可能。
4. モバイル幅（<=640px）で1カラム表示が維持。
