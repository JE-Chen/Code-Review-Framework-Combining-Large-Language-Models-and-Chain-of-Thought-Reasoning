# 研究資料封存說明

本目錄彙整 `paper/論文_v3.21.docx` 所使用或討論的資料集、模型輸出、評分結果與重現程式。資料於 2026-07-21 建立初始快照，並於 2026-07-22 更新 RAG 開關組之完整評分、成對統計及後續消融狀態。固定無關規則組仍在執行，因此本目錄不是全部消融實驗的最終封存版本。

## 目錄結構

| 路徑 | 內容 |
|---|---|
| `datasets/code_to_detect/` | 44 筆 Python 合成評估案例。 |
| `datasets/fine_tuning_data/` | Gemma LoRA 使用的 695 筆訓練資料及資料產生提示。695 筆全部作為 train，validation 與 test 均為 0。 |
| `datasets/RAG_data/` | 相關規則、無關規則及 RAG 語料選擇程式。 |
| `experiment_inputs/Prompts/` | 審查與評分提示。 |
| `experiment_outputs/Results/` | 各模型、提示詞與 RAG 條件的實驗輸出、評分與日誌。 |
| `experiment_outputs/Responses_No_RAG_Finetune/` | 前代模型在無 RAG／微調相關條件下的回覆資料。 |
| `analysis/Compare/` | 比較分析資料。 |
| `reproducibility/scores/` | 參考問題建立、推論重放、問題覆蓋與彙整程式。 |
| `reproducibility/deployment/` | Gemma 服務與 RAG／LoRA 消融部署設定。 |
| `EXPERIMENT_RESULTS_TABLES.md` | 已定案量化結果、RAG 命中稽核、RAG 開關組成對統計及消融實驗進度表。 |
| `REVIEWER_ISSUES.md` | 論文修改建議的最新修訂對照表。 |

## 44 案評估資料與參考問題集

- 44 筆評估案例位於 `datasets/code_to_detect/`。
- 333 個參考問題分散於 `experiment_outputs/Results/2026-07-19-gemma4-experiment/ground_truth/` 的 44 份 JSON。
- 每個參考問題包含 `id`、`desc`、`category` 與 `severity`。
- 參考問題由 `gpt-5.6-sol` 僅讀取原始碼後建立，屬模型產生的參考問題集，不是人工標註黃金標準。
- 建立程式為 `reproducibility/scores/codex_groundtruth.py`，執行紀錄為上述 `ground_truth/gt.log`。

## 問題覆蓋與宣稱正確性

每個案例的評分目錄包含兩類不同統計：

- `coverage.json`：記錄命中的參考問題 ID，用於計算參考問題涵蓋率，例如多階段為 197／333。
- `precision.json`：記錄審查輸出中的問題宣稱數、成立數與錯誤宣稱，用於計算問題宣稱正確率，例如多階段為 474／480。

兩者的分子不是同一個計數單位，因此 `474／480` 應解讀為問題宣稱正確率，而不是與 `197／333` 共用 true-positive 分子的傳統分類精確率。若將兩者計算調和平均，應稱為描述性調和平均，不應直接視為標準分類 F1。

## 快照時的實驗狀態

詳細資料見 `SNAPSHOT_STATUS.json`。

- 相關規則檢索／多階段：44／44 完成。
- 停用檢索／多階段：44／44 完成。
- 單一提示詞：44／44，完成。
- RAG 開啟／關閉獨立五維評分：88／88 完成。
- 無關語料檢索診斷：已停止，20 案成功、6 案逾時，成功案例皆為零命中，不作為品質消融結果。
- 固定無關規則直接注入：12／44 完成，每案固定注入 3 條無關規則，實驗中。
- 全規則直接注入：尚未執行。
- 未掛載 LoRA 的 Gemma 基礎模型：尚未執行。

## 人工評分資料

本快照包含 `experiment_outputs/Results/2026-07-20-human-rating-audit.json` 所彙整的人工評分判讀。人工評分共 8 份有效回覆，分別來自 8 名不同評分者，現有資料定位為前代模型組態的描述性歷史對照。

## 完整性與敏感資訊

- `MANIFEST.sha256` 記錄本快照各檔案的 SHA-256。
- 建立快照前已檢查常見憑證檔名、API 金鑰、GitHub token、AWS access key 與私鑰格式，未發現符合項目。
- 本目錄可能包含合成程式碼、模型回覆、公開服務主機名稱及本機專案路徑，公開發布前仍應進行人工複核。








