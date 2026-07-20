# 論文 v3.8 → v3.9 變更紀錄（整合定稿）

本檔記錄由 `paper/論文_v3.8.docx` 產出 `paper/論文_v3.9.docx` 之修訂。
第一批處理**與實驗資料無關**之修訂（冠穎 review 中不需重跑實驗即可更正者），
每一項皆可溯源至程式碼、score 檔或原文段落，**未新增或更動任何實驗數據**。
產出方式：`paper/_rewrite_v3_9.py`（原檔不動），並重生 `paper/_dump_論文_v3.9.txt`
與表格 dump，通過 `paper/_check_rules.py`。

## 第一批原列之待辦（已由資料相依批次接續處理）

- 表七–表十三（全部）之重構、刪併與欄名正名。
- 消融 +34／+2 之改寫與「折算／三分之一量級」措辭。
- §5.3.2（[0475]，邊際效益）、§5.3.3（[0477]／[0478]，與 CRSCORE++ 對照）整段，
  含其 `completeness` 用詞與「全面提升／優於」等 RQ1 措辭，**本批次完全未動**。
- 表六之公平性降級（「優於」→描述性對照）與 RQ1 結論改述。
- 結論三層化（§6.1／§6.2）與任何依賴消融差值之結論句。上述項目均已於下列資料相依批次處理。

---

## 問題 #s7：封面年份與英文年份不一致
- 審查意見（問題）：封面「中華民國一一六年六月」與英文「June, 2026」矛盾（116 年為 2027）。
- 對應更改：封面中文年份改為「一一五」（民國 115 年＝西元 2026 年），與英文 June, 2026 一致。
- 依據/來源：原文 [0013] 與其下一行 [0014]「June, 2026」；純曆法換算，無實驗資料。
- Before → After：
  - Before: `中 華 民 國 一一六 年 六 月`
  - After: `中 華 民 國 一一五 年 六 月`

## 問題 #s4：§1.5 貢獻計數自相矛盾
- 審查意見（問題）：[0095] 述「七項＝前三核心＋後四設計」，[0099] 卻寫「下列三項…設計貢獻」。
- 對應更改：[0099]「下列三項」改為「下列四項」，其後確為第 4–7 項共四項設計貢獻。
- 依據/來源：原文 [0095]「後四項為隨附開源框架之設計貢獻」；[0100]–[0103] 為第 4、5、6、7 項。
- Before → After：
  - Before: `下列三項屬於本研究隨附之開源框架之設計貢獻…`
  - After: `下列四項屬於本研究隨附之開源框架之設計貢獻…`

## 問題 #s2：目錄由 3.3.9 跳至 3.5（缺 3.4）
- 審查意見（問題）：章節目錄自 3.3.9 直接跳至 3.5，遺漏 3.4。
- 對應更改：根因為內文 §3.4 標題段缺 `outlineLvl`（同層之 §3.5 有 `outlineLvl=1`），
  故 TOC 生成時被漏收。已為 §3.4 標題補 `outlineLvl=1` 與 `_Toc` 書籤，並於目錄快取
  之 3.3.9 與 3.5 之間補回「3.4 程式碼審查流程」條目（超連結／PAGEREF 指向新書籤）。
- 依據/來源：內文 §3.4 標題（[0230] 程式碼審查流程）；比對同層 §3.5／§3.6 之 `outlineLvl`。
  頁碼填 46（§3.4 之圖三於圖次目錄列為第 46 頁），為快取值，Word 更新功能變數時自動重算。
- Before → After：
  - Before: `…3.3.9 全局規則提示詞  43 → 3.5 與程式碼編輯環境整合  48`
  - After: `…3.3.9 全局規則提示詞  43 → 3.4 程式碼審查流程  46 → 3.5 與程式碼編輯環境整合  48`

## 問題 #s6：口語化與非正式措辭
- 審查意見（問題）：多處以「直覺先行：」「所以呢：」等標籤式口語開頭，及「塞進提示詞」
  「考自己擅長之題」等非學術用語。
- 對應更改：移除全部 11 處「直覺先行：」標籤（§3.3.1–§3.3.9、§3.5、§4.1），改以正式引導句，
  白話直覺內容全數保留；§5.3.1 之「所以呢：」（[0471]）改為正式陳述句
  （§5.3.2／§5.3.3 之「所以呢：」依指示保留不動）；「把整段審查塞進一個提示詞」與
  RAG 之「塞進提示詞」改為正式用語；「考自己擅長之題」整句改寫。
- 依據/來源：原文各段（[0083]、[0125]、[0184]–[0240]、[0375]、[0471]）；純措辭層。
- Before → After：
  - Before: `直覺先行：與其要模型一口氣把整段審查做完，不如…`
  - After: `就審查流程之設計而言，與其要模型一口氣把整段審查做完，不如…`
  - Before: `把整段審查塞進一個提示詞，正是輸出不穩定與幻覺的溫床`
  - After: `將全部審查任務置於單一提示詞，正是輸出不穩定與幻覺的溫床`
  - Before: `也不能全由單一模型生成而讓受測者「考自己擅長之題」`
  - After: `也不能全由單一模型生成，以避免受測模型評測其自身偏好之題型`
  - Before: `所以呢：兩套獨立評審（自動 + 人工）在多數深層維度上指向同一結論`
  - After: `由上述一致性檢核可知，兩套獨立評審（自動 + 人工）在多數深層維度上指向同一結論`

## 問題 #9／#10：知識蒸餾定義過寬、think 欄未納入 loss 之更正
- 審查意見（問題）：#9 知識蒸餾定義應收斂（本研究非 Hinton soft-target 蒸餾）；
  #10 不應宣稱學生「學到逐步推理」，因 think 欄實際未進入訓練損失。
- 對應更改：
  §2.9 [0141] 補明本研究採「回應式蒸餾（response-based distillation）／指令蒸餾」，
  僅以教師回應（答案）作 SFT，未取用教師 logits／soft target／溫度蒸餾損失，與
  Hinton soft-target 蒸餾有別。
  §2.9 [0143] 刪除「使學生模型學到的是『如何逐步推理地審查』」，改述學生僅以最終審查
  答案（answer 欄）為監督訊號，think 欄存於資料集卻未納入損失，故不宣稱習得教師推理軌跡，
  逐步可追溯來自推論時之管線結構（§3.3）。
  §3.2.1 [0177] 補一句：訓練輸入模板為 `build_prompt(instruction, question)`，訓練目標為
  answer 欄，think 欄不參與提示組建亦不計入損失。
- 依據/來源：`codes/train/qwen3-coder-30b.py`、`gemma-4-31b-it.py`：
  `build_prompt(instruction, question, think)` 之 `think` 標註 `unused`（`# think kept to
  match dataset field`），且 `label = [-100]*prompt_len + full_ids[prompt_len:]`
  （`# only answer tokens get loss`）；Hinton 為既有引用 [22]。
- Before → After：
  - Before: `…使學生模型學到的是「如何逐步推理地審查」，而非死記答案…`
  - After: `…僅以教師之最終審查答案（即資料集之 answer 欄）作為監督訊號進行 SFT，訓練目標
    僅涵蓋 answer 欄，think 欄雖存於資料集卻未納入損失（詳見 §3.2.1）…而非權重內化之推理。`
  - Before: `（§3.2.1 無 build_prompt 說明）`
  - After: `訓練輸入模板為 build_prompt(instruction, question)，訓練目標為 answer 欄，
    think 欄雖為資料集之一欄，但既不參與提示組建亦不計入損失。`

## 問題 #7：表四把訓練量化誤列為推論參數
- 審查意見（問題）：表四將 `load_in_4bit=True`（QLoRA 訓練量化）列於「推論階段生成參數」。
- 對應更改：表四於單一表號內拆為兩段標示：「訓練量化配置（QLoRA）」（load_in_4bit、
  bnb_4bit_use_double_quant、bnb_4bit_quant_type=nf4、bnb_4bit_compute_dtype=torch.bfloat16）
  與「推論配置」（bf16 載入、SDPA 注意力、do_sample=False 貪婪解碼、temperature=None、
  top_p=None、max_new_tokens=32768、repetition_penalty 未設定）。標題與說明文字同步更正，
  說明改述「推論採貪婪解碼，未使用 temperature／top_p 取樣」。表五以後表號不變。
- 依據/來源：訓練量化來自 `codes/train`（QLoRA BitsAndBytesConfig）；推論配置來自
  `codes/util/hf_model_util.py`（`torch_dtype=torch.bfloat16`、SDPA、`do_sample=False`、
  `temperature/top_p/top_k=None`、`_DEFAULT_MAX_NEW_TOKENS=32768`、無 repetition_penalty）。
- Before → After：
  - Before: `表四、模型程式碼審查生成參數設定`（6 列，load_in_4bit 與 max_new_tokens 混列）
  - After: `表四、模型訓練量化與程式碼審查生成參數設定`（14 列，訓練量化／推論兩段標示）
  - Before（說明）: `本表列出推論階段…生成參數（如 temperature、top_p、max_new_tokens 等）…`
  - After（說明）: `…推論以 bf16 載入權重並採 SDPA 注意力，解碼採貪婪策略（do_sample=False），
    未使用 temperature／top_p 取樣，亦未設定 repetition_penalty…`

## 問題 #8：CRSCORE++ 正規化說明缺漏、用詞不一致
- 審查意見（問題）：表六數值為 0–1，但未說明 1–5 分如何正規化；且摘要用 `completeness`、
  表六用 `comprehensiveness`，同一維度用詞不一。
- 對應更改：於 §4.2.2（表六計分定義處）補正規化說明：**此 1–5 分至 0–1 之正規化為
  CRSCORE++ 於其原始論文即定義之尺度（1 分對應 0.2、5 分對應 1.0），非本研究所執行**，
  表六即依 CRSCORE++ 此一正規化尺度呈現。用詞方面，將**摘要**（中文 [0022]、英文 [0030]）
  之 `completeness` 統一為 `comprehensiveness`，與表六一致。
- 依據/來源：`datas/Results/2026-06-11-gemma4-31b/score.md` 註記「normalize 0~1,1=0.2」
  與「normalize 0~100,1=20」為沿用 CRSCORE++ 原始正規化尺度之紀錄；該檔維度名亦為
  comprehensiveness。正規化之來源歸屬（CRSCORE++ 原始論文，非本研究）依作者確認。
- Before → After：
  - Before: `…最後於三個維度各給 1–5 分。Comprehensiveness 表示…`
  - After: `…最後於三個維度各給 1–5 分。CRSCORE++ 於其原始論文即將 1 至 5 分之評等正規化至
    0 至 1 區間（1 分對應 0.2、5 分對應 1.0），表六所列即依 CRSCORE++ 此一正規化尺度呈現。…`
  - Before: `二者於三維度相當（completeness 皆 1.00，conciseness 0.79 對 0.78…）`
  - After: `二者於三維度相當（comprehensiveness 皆 1.00，conciseness 0.79 對 0.78…）`

## 問題 #11：CoT 與多階段工作流之定位、可解釋性宣稱
- 審查意見（問題）：應釐清「CoT」與「多階段工作流」，且中間文字理由不等同模型真實內部推理，
  不應作為忠實可解釋性之直接證據。
- 對應更改：於 §3.3.1 補明本研究之方法宜稱為「多階段結構化審查工作流
  （multi-stage structured reasoning workflow）」，CoT 僅為其中一種提示策略；並明言各階段
  之文字理由不必然反映模型真實內部推理，亦不足以作為忠實可解釋性之直接證據，可追溯性
  來自各階段產物落檔與流程結構，而非權重內化推理之忠實映射（與 §2.9 [0143] 之更正呼應）。
- 依據/來源：原文 §3.3.1 [0184]；論述層修訂，無實驗資料。
- Before → After：
  - Before: `…這正是本研究回應「輸出不穩定」問題之結構性手段。`
  - After: `…之結構性手段。更精確地說，本研究之方法宜稱為多階段結構化審查工作流
    （multi-stage structured reasoning workflow），CoT 僅為其中一種提示策略。須留意的是，
    各階段輸出之文字理由並不必然反映模型真實之內部推理，亦不足以作為模型忠實可解釋性之
    直接證據…而非模型權重內化推理之忠實映射。`

---

## 資料相依定稿批次（2026-07-19 Gemma 重放）

### 問題 #2：以無法重現之 +34／+2 回答邊際效益
- 更改：刪除 +34／+2、折算與「三分之一量級」之主結果論述，改以表八之 Recall、Precision、F1、嚴重度加權 Recall、逐類與逐案比較回答 RQ2／RQ3。
- 依據：`datas/Results/2026-07-19-gemma4-experiment/{multi_rag_on,single}/cot/*/{coverage,precision}.json` 與 `ground_truth/*.json`。
- Before → After：`流程 +34、微調 +2` → `Recall 0.592 對 0.498、Precision 同為 0.988、F1 0.740 對 0.663；逐案 26 勝、14 平、4 負`。

### 問題 #3：結論超過資料所能支持的範圍
- 更改：§5.3 與 §6 改成已實證、初步支持、尚待驗證三層。明載前次沿用閾值 0.7 時 0／44 命中，改用 EmbeddingGemma 校準閾值 0.32 後為 25／44 案命中、合計 133 份規則文件，惟命中不等同品質提升。Gemma 微調無 base-model 端點可供乾淨消融，不再主張三者缺一不可。
- 依據：`datas/Results/2026-07-20-rag-hit-audit.json`、`codes/run/embedding_threshold_calibration.md` 與現行服務部署限制。

### 問題 #4–#6：舊五維表重複、欄名混淆與人工結論過度
- 更改：刪除舊表七至表十一之 GPT-5／Gemini-3 自動表，新增現行 Gemma 之 Claude／gpt-5.6-sol 雙裁判表。原人工表改編為表十與表十一並標示前代 Qwen 配置，表十欄名改為「多階段提示詞／單一提示詞」，不再混用 Ours／Base model，微調人工結果僅陳述 Maintainability 與 Correctness 小幅正向，其他三維未一致改善。
- 依據：`our_score_claude.md`、`our_score_gpt56sol.md` 逐案 44 份及原人工表既有數值。

### 問題 #7／#8：生成參數與 CRSCORE++ 尺度
- 更改：表五分列現行 Gemma 訓練入口預設之 bf16 LoRA、前代 Qwen QLoRA 與現行服務推論組態，補 do_sample、temperature、top_p、repetition_penalty 與環境快照未保存之限制，§4.2.2 明列正規化分數＝原始評等／5。
- 依據：`docker/docker-compose.train.yml`、`codes/train/gemma4-31b.py`、`docker/docker-compose.server-gemma4.yml` 與既有 CRSCORE++ 評分紀錄。

### 實驗問題 #1：RAG 消融退化
- 更改：確認前次 0.7 閾值屬前代 Qwen 嵌入設定，對 EmbeddingGemma 造成 0／44 退化結果。以校準閾值 0.32 重測檢索後，25／44 案命中、合計 133 份文件。生成層 44 案重放另存於 `datas/Results/2026-07-20-gemma4-rag-calibrated/`，完整評分完成前不宣稱 RAG 提升品質。

### 實驗問題 #2：CRSCORE++ 比較不公平
- 更改：表七降級為描述性對照，明載基準欄與 Ours 欄之裁判及資料不同，§5.3.3 與結論均不以表七回答 RQ1。

### 實驗問題 #3：44 案統計與泛化限制
- 更改：新增表二，列 44 案資料夾來源標籤、類型、LOC、333 個 model-derived reference 問題、嚴重度分布與第七／第八案重複，§6.3 明載未保存生成模型確切版本與完整提示 provenance、去重後 43 筆、合成資料與單一基準限制。
- 依據：`ground_truth/*.json`、案例原始碼與 `code_to_detect`。

### 人工評分 CSV 與教師版本補證
- 人工評分 CSV 可確認 8 份有效回覆，每份對三組方法各評五個維度。完整多階段組與單一提示詞組之五維平均為 85.6 與 79.25，逐份比較為 6 勝、2 負；兩個多階段組平均為 85.6 與 85.4，逐份比較為 4 勝、4 負。
- 作者確認 8 份回覆分別來自 8 名不同評分者。CSV 仍無評分者識別碼與案例編號，身分不能由檔案獨立核驗，且評分手冊要求自行隨機抽案例，故不能對不同案例計算正式 ICC。背景與年資未記錄；方法資料夾名稱揭露條件，故不宣稱盲評；僅案例抽選可確認，方法呈現順序未見隨機化紀錄。
- 稽核結果與來源 SHA-256 保存於 datas/Results/2026-07-20-human-rating-audit.json。
- 作者確認教師模型確切版本為 ChatGPT 5.4。論文已更新所有「教師版本未留存」敘述；仍保留逐筆生成 provenance、教師參數規模、資料清理、token 數、loss 曲線、checkpoint、峰值 VRAM 與訓練時間未完整歸檔之限制。

### 工程部署圖與可重放消融組態
- 新增圖二「工程部署架構圖」，原訓練、程式碼審查與 LLM-as-a-Judge 圖順延為圖三至圖五；圖次目錄與正文交叉引用同步。可維護來源為 datas/Architecture/v3.9/工程部署架構.drawio，另提供 SVG／PNG 與重生腳本。
- 服務新增 PRTHINKER_RAG_MODE=retrieval|all|off、PRTHINKER_RAG_CORPUS=relevant|irrelevant 與 PRTHINKER_DISABLE_LORA=1。/healthz 回報模型、RAG 模式、語料名稱、語料 SHA-256 與 LoRA 狀態。
- 新增三份 Compose 疊加設定，分別供無關規則、全規則直接注入與 Gemma base-model 組重部署。實驗驅動器會在首案前核對健康檢查並保存 server_manifest.json，避免批次混入不同服務版本。
- 相關 Python 編譯、三份 Compose config 與 33 項單元測試均通過。44 案生成與評分尚待重部署後執行，論文只寫「組態已完成」，不預寫任何消融結果。

### 訓練資料與硬體證據更正（2026-07-20）
- 程式庫提交前資料為 663 個實體行，其中 8 行串接多個 JSON 物件而非有效 JSONL。修復後現行檔為 695 筆有效 JSON，其中 5 筆完全重複。
- Gemma 轉接器評估報告時間早於修復提交，但 Git 提交時間不能排除修復內容曾以未提交狀態先供訓練使用。因未保存訓練資料 hash、快照或 console log，論文不再宣稱實際訓練為 663 或 695 筆。
- 現行入口只建立 train dataset，沒有 validation／test。表三所列超參數改標為「現行入口程式預設」，因實際環境覆寫快照未保存。
- 前代 Qwen 環境紀錄為雙 L40S，現行 Gemma Compose／Dockerfile 則以 DGX Spark GB10 為目標平台，兩代不再混寫。該次 Gemma 訓練之實際硬體快照與峰值 VRAM 無法確認。
- 現行 Gemma 訓練入口為 `docker/docker-compose.train.yml` 所呼叫之 `codes/train/gemma4-31b.py`，預設 bf16 LoRA；`codes/train/gemma-4-31b-it.py` 為另一條 QLoRA 腳本，不能混作本次入口。
