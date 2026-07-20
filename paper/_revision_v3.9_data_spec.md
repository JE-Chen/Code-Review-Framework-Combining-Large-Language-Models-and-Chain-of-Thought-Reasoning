# v3.9 資料相依定稿 — 權威數據 + 改寫指令
所有數字皆可溯源至 datas/Results/2026-07-19-gemma4-experiment/。不捏造。基準檔 paper/論文_v3.9.docx（已含資料無關批次）→ 就地續改為最終 v3.9（走 python-docx 腳本；原檔不動；重生 dump + _check_rules）。

## 實驗 provenance（寫入 §4/§5 方法）
- 2026-07-19 於現行部署伺服器（Gemma-4-31B-it + 未合併 LoRA，pr-thinker-2）對 §4.1 之 44 筆合成 Python 案例端到端重放。
- 兩條件：多階段（/review，五步驟 CoT）與單一提示詞（/ask，SINGLE_CODE_REVIEW_PROMPT）。同一基座、同一資料、貪婪解碼。
- 評估分兩層：
  (A) LLM-as-a-Judge 五維主觀品質（Claude Opus 4.8 與 gpt-5.6-sol 雙裁判）。
  (B) 客觀問題偵測：ground truth 由 gpt-5.6-sol 只讀程式碼獨立列出（333 個真問題），Claude 交叉比對各管線之覆蓋。
- 限制（誠實寫入）：ground truth 與比對皆為 LLM 產生，非人工黃金標準；此為 model-derived reference，人工驗證屬未來工作。

## 資料集統計表（§4.2，回應 #3）
| 項目 | 值 |
|---|---|
| 案例數 | 44（資料夾標記 ChatGPT 22 + Copilot 22；確切模型版本與生成參數未保存）|
| 類別 | bad_data 4、code_diff 12、only_code 28 |
| LOC（非空白）| 總 3241、平均 73.7、中位 65、min 37、max 150 |
| GT 真問題 | 總 333、平均 7.6/案、min 1、max 17 |
| 嚴重度分布 | critical 7、high 60、medium 181、low 85 |
| 唯一性 | cot_chatgpt_only_code_7 與 _8 原始碼 byte-identical（重複）→ 實為 43 unique |
（LOC/GT 逐案值見 ground_truth/*.json 與 code_to_detect；如需逐案表可加附錄。）

## 表 (B)：客觀問題偵測（取代舊「+34/+2」為主結果）
n=44、333 真問題。多階段用完整 findings（first_summary+first_code_review+linter+code_smell+total_summary），單提示詞用其單一審查。
| 指標 | 多階段 | 單一提示詞 |
|---|---|---|
| Recall | 0.592（197/333）| 0.498（166/333）|
| Severity-weighted recall | 0.602 | 0.510 |
| Precision | 0.988（474/480）| 0.988（329/333）|
| F1 | 0.740 | 0.663 |
| 平均宣稱/案 | 10.9 | 7.6 |
逐案（recall 比較）：多階段勝 26、平 14、單提示勝 4。
per-category recall（多階段/單提示）：correctness 0.489/0.387、bug 0.522/0.403、security 0.571/0.476、smell 0.815/0.630、maintainability 0.763/0.738、design 0.000/0.000（唯一 1 題兩者皆未命中）。→ 五個有命中類別多階段皆較高，design 類持平。

## 表 (A)：LLM-as-a-Judge 五維主觀品質（誠實並陳；final review = total_summary vs single review）
Δ = 多階段 − 單提示，逐維（Readability/Maintainability/Correctness/Multi-Review-Coverage/Comprehensiveness）：
- Claude（n=44）：多階段均 78.8、單提示 83.8；Δ −2.3/−6.9/−0.3/−9.3/−6.3，per-dim avg −5.01。
- gpt-5.6-sol（n=44）：多階段均 84.4、單提示 86.0；Δ −0.3/−0.5/+1.5/−7.7/−1.0，per-dim avg −1.60。
誠實敘述：主觀 prose 品質上單提示詞相當或略佳（其輸出為單一連貫文件、含 refactor 範例）；多階段唯 correctness 打平/略勝。此與客觀 recall 結論並不矛盾：多階段贏在「找到更多真問題」，單提示贏在「呈現」。評分對表示法/裁判敏感（回應 #3 之 LLM-judge 可靠度疑慮）。

## 表六 CRSCORE++（沿用 v3.8 數值，僅改敘述，#2/exp#2）
數值不動（comprehensiveness 0.67/1.00/1.00/0.97、conciseness 0.57/0.79/0.78/0.69、relevance 0.63/0.86/0.86/0.79）。改寫：CRSCORE++ 基準由 GPT-4o-mini 於其原始資料評分、Ours 由 Claude 於本研究 44 案評分，judge 與資料皆不同→降級為「描述性對照」，刪「優於／全面提升」，RQ1 不以表六作答。

## RAG（exp#1）
前次沿用前代 Qwen 嵌入閾值 0.7，於 44 案之命中為 0／44，屬設定不相容造成之退化結果。EmbeddingGemma 校準閾值 0.32 之獨立檢索稽核為 25／44 案命中、合計 133 份規則文件，來源為 `datas/Results/2026-07-20-rag-hit-audit.json`。命中不等同規則相關或審查品質提升，完整生成重放與客觀評分完成前不主張 RAG 有效或必要。

## 訓練資料與執行證據
- 現行入口：`docker/docker-compose.train.yml` → `codes/train/gemma4-31b.py`，程式預設為 `google/gemma-4-31B-it`、bf16 LoRA。
- 提交前資料：663 個實體行，其中 8 行串接多個 JSON 物件而非有效 JSONL。現行資料：695 筆有效 JSON，其中 5 筆完全重複。
- 實際訓練筆數：不可判定。評估報告與修復提交之時間序不能排除未提交工作目錄已先修復，且未保存資料 hash、快照或 console log。
- 切分：入口只建立 train dataset，validation／test 皆不存在，實際 train 筆數不可判定。
- 表三超參數為現行入口程式預設，不是由該次訓練日誌確認之執行值。作者確認教師為 ChatGPT 5.4；逐筆生成 provenance、token 總數、loss 曲線、checkpoint 實體、峰值 VRAM 與訓練時間均無法由現存庫重建。
- 硬體：前代 Qwen 環境紀錄為雙 L40S；現行 Gemma Compose／Dockerfile 以 DGX Spark GB10 為目標平台，但該次執行硬體快照未保存。

## 微調消融（#2 exp、限制）
本輪已完成結果使用掛載 LoRA 的 Gemma。服務程式現已具備 `PRTHINKER_DISABLE_LORA=1`，可重部署 base-model 組，但相同 44 案尚未完成重放與評分，故微調獨立效益仍列為待驗證。

---

# 改寫指令（就地改 v3.9）

D1. §5.2/§5.3 表格重構：**刪除舊表七–表十三**（Qwen 前代、無來源之 5 維 GPT-5/Gemini 數字）。新增：
  - 新表：客觀問題偵測（上表 B，recall/precision/F1/severity-weighted + per-category + 逐案 26-4-14）— 作為 RQ2/RQ3 主證。
  - 新表：LLM-as-a-Judge 五維主觀（上表 A，Claude 與 sol 雙裁判 Δ）— 誠實並陳。
  - 人工表（原表十二/十三，Qwen 前代人工評分）：明確標為「前代 Qwen 配置之人工評分」，不與 Gemma 客觀結果混用；或移附錄。
  - 表六保留、僅改敘述（見上）。重編表號、目錄、交叉引用。

D2. §5.3.2「邊際效益」整段（[0473-0475]，含 +34/+2/折算/三分之一量級/所以呢/可砍掉微調）：**全刪重寫**為客觀 bug-detection 主結果：多階段 recall 0.592 vs 0.498（+9.3pp，多 19% 真問題）、precision 相同 0.988、F1 0.740 vs 0.663，每類皆勝；其優勢源於專屬 linter/code_smell 階段。並誠實並陳 LLM-judge prose 主觀品質相當/單提示略勝（表 A），說明兩指標互補（多階段贏抓 bug、單提示贏呈現）。

D3. §5.3.3 與 RQ1（[0477-0478]，含「所以呢」「全面提升」）：改為表六描述性對照、RQ1 不以此作答。

D4. RQ2/RQ3 重定義（§1.3/§5.3）：多階段之邊際貢獻 = 問題偵測完整性（recall/F1 較高、precision 不降），非 prose 美感。

D5. 結論三層化（§6.1/§6.2，#3）：
  - 已實證：於 44 案客觀評測，多階段之問題偵測 recall/F1 高於單一提示詞（precision 相同）。
  - 初步/相當：主觀 prose 品質兩者相當，單提示於呈現略佳；微調於前代自動評分有小幅改善。
  - 尚待驗證：RAG 獨立效益（本資料退化）、微調於現模型之乾淨消融、人工黃金標準、真實 PR 泛化、幻覺率、一致性、成本效益。刪「三者缺一不可」「可用→可信賴之關鍵」。

D6. §4.2 新增資料集統計表（上表）+ 揭露 7≡8 重複。§6.3 限制補：合成資料、model-derived ground truth、43 unique、單一基準。

D7. 全程 paper_rule：無破折號子句、全形標點、無 AI 口頭禪、繁體；每個數字對回 datas/Results/2026-07-19-gemma4-experiment/。標「本論文之客觀評測」為新增內容。

完成後：重生 paper/_dump_論文_v3.9.txt 與表格 dump；跑 paper/_check_rules.py；更新 paper/CHANGES_v3.9.md（新增資料相依批次章節，逐項 問題→更改→依據→before/after）；回報逐項與任何無法溯源之處。
