# 論文 v3.8 → v3.9 修訂規格（依 冠穎 review；不捏造，數字皆可溯源）

來源 review：論文修改建議-冠穎.docx（本機外部檔案，未納入儲存庫）
規則：D:\Codes\ThesisAgents\.claude\agents\rules\paper_rule.md（不捏造最高優先）＋ paper/REWRITE_BRIEF.md ＋ paper/_check_rules.py
基準檔：paper/論文_v3.8.docx（不改原檔，產出 paper/論文_v3.9.docx，並重生 _dump 與 _dump_tables）

## 唯一權威數據（真實 Claude 重評分，n=44，單一 judge=Claude Opus 4.8）
來源：132 × datas/Results/{2026-02-15 ours, 2026-02-27 base(no-ft-no-rag), 2026-02-28 single(no-any-steps)}/cot/*/our_score_claude.md
逐維平均（0–100，序：Readability, Maintainability, Correctness, Multi-Review Coverage, Comprehensiveness）：
- Ours (multi+RAG+FT):   82.55, 83.80, 80.30, 84.50, 84.82
- Base (multi, no-RAG/no-FT): 81.41, 83.36, 78.00, 83.93, 84.75
- Single Prompt:         78.00, 74.64, 75.61, 53.18, 59.91

邊際貢獻公式（明確、供 #2）：各維取 44 案平均，單一 judge、等權，component 邊際貢獻 = mean(Ours) − mean(對照)，**逐維報告並取逐維平均；不得跨維相加、不得換算成「三分之一量級」**。
- 多階段結構（Ours − Single）：R+4.55 / M+9.16 / Corr+4.68 / Cov+31.32 / Comp+24.91；逐維平均 **+14.9**
- 純多階段（Base − Single）：逐維平均 **+14.0**（Cov+30.75、Comp+24.84 為主）
- RAG＋微調增量（Ours − Base）：R+1.14 / M+0.43 / Corr+2.30 / Cov+0.57 / Comp+0.07；逐維平均 **+0.9**（各維 <+2.3）

---

## A. 資料整合類（表七–表十三 + 敘述）

### A1 表格重構（#2 #4 #5）
現況：表七(GPT-5 prompt)/表八(Gemini prompt)/表九(Gemini vs base，標題誤標「提示詞設計」)/表十(GPT-5 vs base)/表十一(Gemini vs base，與表十逐格相同=複製錯誤)/表十二(人工 prompt)/表十三(人工 finetune)。
改為單一 judge=Claude，兩張 LLM 表 + 兩張人工表：
- **表七（LLM-as-a-Judge-Our，Claude）：多階段提示詞 vs 單一提示詞**（欄名 = Multi-stage Prompt / Single Prompt，回應 #5）
  | 維度 | Multi-stage Prompt | Single Prompt |
  | Readability | 82.55 | 78.00 |
  | Maintainability | 83.80 | 74.64 |
  | Correctness | 80.30 | 75.61 |
  | Multi-Review Coverage | 84.50 | 53.18 |
  | Comprehensiveness | 84.82 | 59.91 |
- **表八（LLM-as-a-Judge-Our，Claude）：微調 vs 基礎模型**（欄名 = Fine-tuned / Base model）
  | 維度 | Fine-tuned | Base model |
  | Readability | 82.55 | 81.41 |
  | Maintainability | 83.80 | 83.36 |
  | Correctness | 80.30 | 78.00 |
  | Multi-Review Coverage | 84.50 | 83.93 |
  | Comprehensiveness | 84.82 | 84.75 |
- **刪除**舊表八(Gemini)/表九/表十/表十一（GPT-5、Gemini 之逐案 5 維數字於 datas/Results 無來源；單一 judge 後亦不需雙裁判表）。人工表（原表十二/十三）順移為新表九/表十，欄名同理正名（新表九：Multi-stage Prompt/Single Prompt；新表十：Fine-tuned/Without Fine-tune）。
- 重編所有表號（表六 CRSCORE++ 不動）、目錄圖表清單、及全文交叉引用（§5.2.2 提及 GPT-5/Gemini/Claude 三裁判者，改為「以 Claude Opus 4.8 為 LLM-as-a-Judge」；刪除雙裁判 robustness 敘述或改為單裁判＋人工交叉驗證）。
- **人工表（新表九/表十）數值不變**（本研究未重跑人工），但其原始問卷後設資料缺失須於 §5.2.3 標示（見 C1）。

### A2 §5.3.2 邊際效益改寫（#2 #6）取代 [0473]-[0475]
以上述公式與真實數字改寫：多階段結構逐維平均 +14.9（主要 Multi-Review Coverage +31.3、Comprehensiveness +24.9）；RAG＋微調增量逐維平均 +0.9（各維 <+2.3，近雜訊）。明列公式（各維 44 案平均之差、單裁判等權、不跨維相加）。刪除「+34」「+2」「折算」「三分之一個量級」。刪除 [0475] 之「所以呢：…可砍掉微調…三者缺一」整段，改為中性陳述：多階段結構為主要增益來源；RAG 與微調之增量於本評估中甚小且無法乾淨分離（base 同時無 RAG 與微調），故本研究**不主張「三者缺一不可」**。

### A3 表十（人工 finetune）敘述改正（#6）
原稱「人工視角驗證微調確實提升整體品質」→ 改為：微調於 Maintainability、Correctness 呈小幅正向，其餘維度（Readability、Multi-Review Coverage、Comprehensiveness）未見一致改善。

### A4 表六 CRSCORE++ 降級（實驗#2）＋正規化（#8）
- 正規化：加公式「CRSCORE++ 原始 1–5 分，正規化為 raw÷5（1→0.2、5→1.0）」（來源：score 檔註記 1=0.2）。統一用詞：全文 comprehensiveness / completeness 擇一（建議一律 comprehensiveness，與五維表一致），摘要與表格對齊。
- 公平性：表六 Ours 由 Claude 評、CRSCORE++ 原欄由 GPT-4o-mini 評、且非同批資料 → §5.3.3 [0477-0478] 與結論**刪除「全面優於／全面提升」**，改為「與 CRSCORE++ 原研究報告數值之描述性對照」；**RQ1 不以表六作正面結論**，改述為「於本研究之 Claude 評分下，完整框架於三維度分數高於 CRSCORE++ 原報告數值，惟因裁判與資料不同，僅屬描述性對照，不構成同基準之優劣宣稱」。刪除 [0478] 之「所以呢：RQ1 得到正面回答…全面提升」。

## B. 訓練方法類（#7 #9 #10 #12）

### B1 表四拆分（#7）
現況：表四把 load_in_4bit=True 列為「推論階段」。實為 QLoRA **訓練**量化。拆為：
- 訓練量化配置：load_in_4bit=True、bnb_4bit_use_double_quant=True、bnb_4bit_quant_type=nf4、bnb_4bit_compute_dtype=torch.bfloat16（來源：codes/train）。
- 推論配置（來源：codes/util/hf_model_util.py）：bf16 載入、SDPA 注意力、do_sample=False（貪婪解碼）、temperature=None、top_p=None、max_new_tokens=32768、無 repetition_penalty、貪婪故無 seed 依賴。
表四說明文字若提及 temperature/top_p，改為「推論採貪婪解碼，未使用 temperature/top_p 取樣」。

### B2 KD 定義收斂（#9）§2.9 [0141-0143]
保留「知識蒸餾」詞，但明確界定：本研究採**response-based / instruction distillation**（教師生成 Instruction/question/think/answer 之合成資料，學生以 SFT 擬合教師「答案」），**未使用教師 logits／soft target／temperature-based distillation loss**，與 Hinton 之 soft-target KD 不同。[0141] 已述「等同 SFT」，據此收斂即可。

### B3 think 未納入 loss 之更正（#10）§2.9 [0143] 與 §3.2.1 [0177]
關鍵事實（來源：codes/train/qwen3-coder-30b.py、gemma-4-31b-it.py）：資料含 think 欄，但 build_prompt/build_user_content 之 think 參數 **unused**，label 遮罩 `[-100]*prompt_len + answer_ids`（註「only answer tokens get loss」），故 **think 不在輸入、亦不在 loss 目標，僅 answer 計 loss**。
- 刪除/改寫 [0143]「使學生模型學到的是『如何逐步推理地審查』，而非死記答案」→ 改為：學生模型以教師之**最終審查答案**為監督訊號（SFT），訓練目標僅涵蓋 answer；think 欄雖存於資料集，但未納入損失，故本研究**不宣稱**學生透過訓練習得教師之推理軌跡。多階段之「逐步可追溯」來自**推論時的管線結構**（§3.3 多階段提示詞），而非權重內化之推理。
- §3.2.1 [0177] 補一句：訓練輸入模板為 build_prompt(instruction, question)，target 為 answer；think 欄不參與損失。

### B4 訓練資料統計（#12，可溯源部分）
可寫（來源 datas/fine_tuning_data/qwen3_train_data.jsonl）：資料筆數 = **695**，每筆四欄（Instruction/question/think/answer），SFT 監督訊號為 answer。
須標「未記錄／未來補」：teacher 模型確切名稱與版本（文中僅「例如 GPT-5 或 Claude」為示例）、主題分布、去重方式、人工清理比例、train/validation 切分、最終 token 數、loss 曲線、checkpoint 選擇、peak VRAM、訓練時間 → 併入 §5.3/§6.3 限制或 §4 之「本研究未記錄」註記，不得捏造。

## C. 結論與主張（#3、#11）

### C1 結論三層化（#3）§6.1/§6.2/§5.3
改為三層陳述：
- 已實證：於本研究 44 案、Claude 五維評分下，多階段結構相較單一提示詞於多數品質維度較高（逐維平均 +14.9）。
- 初步支持：微調於部分自動維度（Maintainability/Correctness）有小幅改善，人工結果差距甚小。
- 尚待驗證：RAG 之獨立效益、幻覺率下降、輸出一致性、可信賴程度、真實團隊審查時間節省、長期採用與成本效益（皆本研究未量測）。
刪除「從可用邁向可信賴之關鍵」「三者缺一不可」等超出證據之語。

### C2 CoT vs 多階段工作流（#11）
主敘述改用「多階段結構化審查工作流（multi-stage structured reasoning workflow）」；CoT 定位為提示策略之一。明確：中間輸出之文字理由**不等同**模型真實內部推理，亦不得作為忠實可解釋性之直接證據；本研究之可追溯性來自**產物落檔與流程結構**，非模型內部推理之忠實映射。

## D. 結構與寫作（#s1–#s7）

### D1 §3.8 精簡（#s1 #s3）
- 正文 §3.8 之未評估研究級擴充（3.8.1–3.8.23）整體移至**附錄**（或系統文件），正文第三章僅保留已實驗驗證之多階段(§3.3)、RAG、微調(§3.2)、評估。
- 新增一張**功能成熟度表**：欄 = 編號 / 名稱 / 是否實作 / 是否評估；逐列列出 §3.8.1–§3.8.23（實際 **23** 子節），並解決「十七項」計數不一致：全文「十七項」改為與表一致之實際數（或明確定義哪 17 項為「研究級」而其餘為部署/輸出層，並在表中標分類）。不得再出現「十七項」與子節數矛盾。

### D2 目錄 3.4（#s2）
檢查目錄由 3.3.9 跳至 3.5，補回 3.4（系統實作）或修正章節編號連續性。

### D3 §1.5 貢獻計數（#s4）[0099]
[0095] 述「七項＝前三核心＋後四設計」，但 [0099]「下列三項屬於…設計貢獻」矛盾 → 改「下列**四項**」，並確認其後確列四項（第 4–7 項）。

### D4 學術語氣（#s6）
- 刪除「所以呢：」開頭 ×3（[0471][0475][0478]），改為正式接續句或直接陳述。
- 「直覺先行：」開頭之各段（多處，§2.x/§3.3.x/§4.1）：保留其「先給白話直覺」之內容（符合 paper_rule 深入淺出），但**移除「直覺先行：」此一標籤式口語開頭**，改為正式引導句（如「就審查流程而言，…」）。
- 「把整段審查塞進一個提示詞」「塞進提示詞」→「將全部審查任務置於單一提示詞」。
- 「可砍掉微調」→ 已於 A2 刪整段。
- 「考自己擅長之題」[0374]→「避免受測模型評測其自身偏好之題型」。
- 全程符合 paper_rule：無破折號作子句連接、全形標點、無 AI 口頭禪、繁體用詞。

### D5 封面年份（#s7）[0013]
「中華民國一一六年六月」→「中華民國一一五年六月」。

## E. 圖（#s5，另由 architecture-diagram-author 處理）
圖一系統架構：推論模型 Qwen3-Coder-30B → Gemma-4-31B-it；拆為「核心研究架構圖（不含 §3.8 十七/23 項擴充）」與「工程部署架構圖」兩張。鏡射程式碼實況，不虛構元件。

## 完成後
1. 重生 paper/_dump_論文_v3.9.txt 與表格 dump。
2. 執行 paper/_check_rules.py（破折號、全形、字體、編號、AI 署名）。
3. 逐項回填本規格之勾稽。
4. 產出 BUCKET C「需作者提供／需重跑」清單（人工評估後設資料、teacher 版本、RAG 五組消融、CRSCORE++ 同基準重跑、訓練 loss/VRAM/切分、真實 PR 資料集）。
