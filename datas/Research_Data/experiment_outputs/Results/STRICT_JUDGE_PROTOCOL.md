# 嚴苛重評協議（CRSCORE++ comprehensiveness 去飽和）

## 動機

先前 judge 對 comprehensiveness 普遍給 5（飽和），原因是本框架的
`step_by_step_analysis` 段落「逐一遍歷 linter + code-smell 清單」生成，
結構上必然覆蓋每個**被工具標記**的主題，故對「是否涵蓋已標記問題」這個寬鬆問法，
答案恆為「是」→ 5。此飽和是框架設計使然，非審查品質差異，因此不具鑑別力。

本協議改採**更嚴苛、更貼近 CRSCORE++ 原意**的問法：comprehensiveness 衡量審查是否
涵蓋該變更**實際引入的全部問題（ground truth）**，而非僅涵蓋靜態分析工具的輸出。

## 評分維度（CRSCORE++ 廣度）

逐案檢查審查是否就以下與該 diff **相關**之維度提出實質意見：

1. 正確性 / bug
2. 安全性
3. 可讀性
4. 可維護性 / 設計（SRP、耦合、設計模式）
5. 效能 / 效率
6. 記憶體耗用
7. 測試 / 文件

「相關」= 該 diff 的程式碼確有觸及此維度（例如無迴圈則效能維度不強制）。

## comprehensiveness 嚴苛標尺（1–5 整數）

- **5**：涵蓋全部相關維度，且**至少有一處超出工具標記清單的獨立洞察**
  （指出 linter/smell 未標記但真實存在的問題）。
- **4**：完整覆蓋全部**被標記**主題與多數相關維度，但**未超出工具輸出**
  （純工具衍生、無獨立廣度）→ 受工具邊界所限，封頂 4。
- **3**：遺漏 ≥1 個對該 diff 明顯相關的維度（例如程式有明顯效能/記憶體疑慮卻未提）。
- **2**：僅覆蓋少數維度。
- **1**：幾乎未涵蓋應提之問題。

## conciseness / relevance

沿用既有 Claude 嚴格判讀（已有變異、未飽和），不重評，逐案沿用
`crscore_score_claude.md`（qwen）／`crscore_score.md`（gemma 原 Claude 評）之該二維度，
僅覆寫 comprehensiveness 為本協議之嚴苛值。

## 輸出

- gemma：每案寫 `crscore_score_strict.md`，格式
  `("comprehensiveness": N, "conciseness": N, "relevance": N)`。
- qwen：每案寫 `crscore_score_strict.md`，同格式。
- 彙總：`score_strict.md`（各維度平均 / 5）。

## 無捏造聲明

本協議僅改變**評分嚴苛度的判讀準則**，不更動任何審查文本、不虛構遺漏。
每案之 5↔4↔3 判定皆基於該案 `total_summary_result.md` +
`step_by_step_analysis_result.md` 之實際內容與其 linter/smell 清單之對照。
若某案審查確實超出工具輸出，誠實給 5；不為湊低均值而捏造遺漏。
