# DESIGN.md

## 1. Overview & Creative North Star
- このファイルは、システム開発プロジェクトの週次報告レポートUIをAIに一貫して生成させるためのデザイン説明書である。
- 対象は週報HTML、ダッシュボード、レビュー用モックアップ、報告画面コンポーネント全般。
- 目指す印象は「信頼できる」「整理されている」「数値とリスクが一目で分かる」。
- UIは業務資料としての落ち着きを保ちつつ、情報の優先順位が自然に伝わることを重視する。

## 2. Design Principles
- 情報優先: 装飾よりも情報の優先順位を明確にする。
- 一目理解: KPI、リスク、次週アクションがファーストビューで分かることを最優先にする。
- 比較容易性: 先週比、領域差、異常値が見比べやすいことを重視する。
- 再現性: 新しい週報画面を追加しても同じ視覚ルールで拡張できることを重視する。
- 低ノイズ: 過剰な装飾や意味のない演出を入れない。

## 3. Colors

### 3.1 Core Palette
- Page Background: #F5F7FB
- Surface: #FFFFFF
- Surface Alt: #EEF3F8
- Border: #D7E0EA
- Primary Ink: #142033
- Secondary Ink: #4E5D72
- Muted Ink: #7B8798

### 3.2 Semantic Palette
- Progress / Good: #1F9D73
- Warning: #E6A700
- Danger / Delay / Critical: #D64545
- Info / Neutral Highlight: #2F6FED
- Risk Accent: #A855F7
- Change Accent: #0F9FB0

### 3.3 Usage Rules
- ベースは明るい背景と白いカードで構成する。
- 色だけで意味を伝えず、ラベルや数値の位置でも意味が分かるようにする。
- 赤は遅延、不具合、重大課題に限定する。
- 領域別識別色は補助的に使い、画面全体を色分けしすぎない。

## 4. Typography

### 4.1 Font Stack
- Headings: "IBM Plex Sans JP", "Noto Sans JP", sans-serif
- Body: "BIZ UDPGothic", "Noto Sans JP", sans-serif
- Numeric / KPI: "IBM Plex Sans", "Inter", sans-serif

### 4.2 Type Scale
- Page Title: 32px / 700 / line-height 1.2
- Section Title: 20px / 700 / line-height 1.35
- Card Title: 15px / 700 / line-height 1.4
- Body: 14px / 400 / line-height 1.7
- Small Meta: 12px / 500 / line-height 1.5
- KPI Number XL: 36px / 700 / line-height 1.1
- KPI Number M: 24px / 700 / line-height 1.15

### 4.3 Typography Rules
- 見出しは詰め気味、本文は読みやすい行間を取る。
- 数値は半角を基本とし、桁区切りを省略しない。
- 1つのカードの中でフォントの種類を増やしすぎない。

## 5. Spacing & Layout

### 5.1 Spacing Scale
- 4, 8, 12, 16, 24, 32, 40, 56

### 5.2 Container Rules
- Desktop max width: 1280px
- Content width: 1120px
- Outer padding: 32px
- Card padding: 20px to 24px
- Grid gap: 16px to 24px

### 5.3 Layout Structure
- 1段目: タイトル、対象期間、更新日時、報告ステータス
- 2段目: KPIサマリーカード群
- 3段目: 管理領域別サマリー
- 4段目: 進捗 / 品質 / リスクの要約領域
- 5段目: 次週アクション
- 6段目: 主要チケット、補足、注記

## 6. Elevation & Depth
- カードは薄い影かボーダーで区切る。
- Shadow: 0 8px 24px rgba(20, 32, 51, 0.06)
- 強い立体感は避け、報告資料としての静けさを優先する。

## 7. Components

### 7.1 Page Header
- 左にページタイトル、右に期間と更新情報を配置する。
- タイトル下には1文要約を置けるようにする。
- ステータスバッジは Draft / Reviewed / Final の3種を許可する。

### 7.2 KPI Cards
- 横並びまたは折り返しで6枚前後配置する。
- 構成は「ラベル」「値」「先週比」「短い補足」とする。
- 重要KPIは完了件数、未完了件数、バグ件数、期限超過件数、実績工数、再オープン件数。

### 7.3 Domain Summary Cards
- タスク管理、内部課題管理、外部課題管理、リスク管理、不具合管理、変更管理を同一フォーマットで表示する。
- 各カードには新規、完了、未完了を必ず表示する。
- アクセント色は見出し線や小バッジ程度に留める。

### 7.4 Section Cards
- 進捗、品質、リスクは独立カードにする。
- セクションの先頭に要約1行、その下に根拠項目を置く。
- 各箇条書きは1項目1メッセージにする。

### 7.5 Risk Panel
- リスクは最も視線が集まる位置に置く。
- Critical / High / Medium の3段階で表示する。
- 各行は「事象」「影響」「対応」を簡潔に並べる。

### 7.6 Action List
- 次週アクションは最大3件。
- 各行の形式は「内容 / 担当 / 期限 / 成功条件」。
- 実行順が分かる番号付きリストにする。

### 7.7 Ticket Table
- 主要チケット一覧は表形式を基本とする。
- 最低列は ID, 件名, 区分, 状態, 担当, 期限, 優先度。
- 行数が多い場合は重要行を優先表示する。

## 8. Charts & Data Visualization
- 棒グラフは領域別件数比較に使う。
- 積み上げ棒は新規 / 完了 / 未完了の比較に使う。
- 折れ線は週次推移がある場合のみ使用する。
- 円グラフは原則使わない。
- 件数が少ない場合はグラフよりカードや表を優先する。

## 9. Interaction & Motion
- 初期表示は短いフェードインのみ許可する。
- Hover演出は120msから160msに統一する。
- 大きな動きや遊びの強いアニメーションは使用しない。

## 10. Responsive Behavior
- Desktop Firstで設計する。
- TabletではKPIカードを2列、Mobileでは1列に落とす。
- Mobileでは KPI → リスク → 次週アクション → その他 の順で並べる。

## 11. Content Tone in UI
- 文言は簡潔で事務的にする。
- リスク表示は煽らず、事象と影響を冷静に示す。
- 良い結果も過度に演出しない。

## 12. Do's and Don'ts

### Do
- KPIをファーストビューに置く
- リスクと次週アクションを近接配置する
- 色よりも情報設計で優先度を示す
- 領域別比較を同一フォーマットで見せる
- 事実データと解釈コメントを視覚的に分離する

### Don't
- ダークで重すぎる管理画面にしない
- 赤や黄色を常用して緊急感を薄めない
- グラデーション背景を多用しない
- KPIカードごとに見た目を変えすぎない
- 装飾アイコンを増やしすぎない

## 13. Suggested Screen Blueprint
- Header
- KPI Summary Row
- Domain Summary Grid
- Progress / Quality / Risk Row
- Next Actions Panel
- Ticket Table / Notes

## 14. AI Implementation Guidance
- UIを生成するときは、このファイルを最優先の視覚ルールとして扱う。
- 週次報告のデータ構造やKPI定義は agent / skill 側を参照し、このファイルでは見た目と情報配置に集中する。
- 新しい画面を追加しても、色、余白、タイポグラフィ、カードパターンはこのファイルを継承する。

## 15. Template Reproducibility Rules (Strict)
- 正本テンプレートは outputs/weekly/mock/index.html と outputs/weekly/mock/style.css。
- 週次HTML/CSSは必ずテンプレート複製を起点にし、データ値差し替えのみを行う。
- DOMの並び順は以下を固定する。
  1) Header
  2) KPI Summary Row
  3) Domain Summary Grid
  4) Test Group
  5) Progress / Cost / Risk / Next Actions
  6) Overdue Ticket / Qualitative Assessment
  7) Member Table
- 単一HTMLタブ化時も「週次報告タブ内のDOM順序」は上記を維持する。

## 16. Frozen Selectors (Do Not Rename)
- .page-shell
- .report-header
- .kpi-grid
- .kpi-card
- .core-domain-grid
- .domain-card
- .test-group-details
- .test-group-grid
- .insight-grid
- .risk-panel
- .action-panel
- .overdue-details
- .ticket-table
- .qualitative-panel
- .member-table

## 17. Allowed vs Forbidden Changes
### Allowed
- 数値、文言、チケットID、表行の追加削除
- 同一セクション内のリスト項目更新
- タブ実装のための最小限クラス追加（tab-switcher, tab-btn, tab-panel）

### Forbidden
- 上記 Frozen Selectors の改名/削除
- セクションの順序変更
- KPIカードの基本構造変更（タイトル/値/差分/注記）
- Domain Gridを5領域以外に変更
- 不要パネル（Blocker/External Dependency/Technical Debt/Decision/Escalation）の追加

## 18. Data-to-UI Mapping Table (Canonical)
| データソース | UIターゲット | 形式 |
|---|---|---|
| weekly_report: KPI | .kpi-grid | 8カード固定 |
| weekly_report: 領域別サマリー | .core-domain-grid | 5カード固定 |
| weekly_report: テストグループ | .test-group-details | details内3パネル |
| weekly_report: 進捗/コスト/リスク | .insight-grid | 4カード（Action含む） |
| weekly_report: 期日超過 | .overdue-details .ticket-table | 展開可能テーブル |
| weekly_report: 定性評価 | .qualitative-panel | 楽観/悲観 |
| weekly_report: 個人別サマリー | .member-table | 列固定テーブル |
| dev_progress_meeting | 会議タブ | 単一HTML切替 |

## 19. Deterministic QA
- 生成後に validate_weekly_output.py を必ず実行する。
- 追加で以下を確認する。
  - Frozen Selectors が全て存在
  - セクション順序が mock と一致
  - モバイル（<=640px）で 1 カラム化される
- FAIL時はHTML再生成ではなく、テンプレート複製起点に戻して差し替えをやり直す。
