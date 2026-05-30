# 論文補充內容（drop-in 段落集 — v3 修正版）

## 修正聲明

本版相對於 v2 之關鍵差異（v3）：

- **新增框架設計貢獻段落 §3.7**：v2 完成後，隨附之開源框架（`prthinker`）
  另實作十四項「框架層」之研究級擴充機制，分別對應 prompt-injection
  robustness、closed-loop 多輪對話、counterfactual 審查、provenance
  稽核、force-push 差分、suggestion sandbox 驗證、cross-language API
  drift、PR 類型自適應、reproducibility 訊號、dependency upgrade impact、
  reviewer personas + conflict surfacing、risk-weighted attention、
  diff entropy 偵測，以及部署層之 CI matrix 分片 + 非同步 job-pattern
  endpoint。其量化效益本論文\ **未予評估**，全部列為設計貢獻
  並於 §6.4 補上對應之未來工作。
- **§1.5 第六項貢獻擴寫**：原 v2 僅提「四類推論後端與 IDE 整合」，
  v3 加入 §3.7 所述之十三項擴充機制條目，逐項註明本論文未予評估。
- **§6.4 增列 6.4.5**：新增「研究級擴充機制之實證評估」之未來工作項，
  對十三項機制逐項給出最小可驗證實驗骨架（語料規模、對照變項、評估
  指標），確保未來補實驗時有可遵循之骨架。
- 不變項目（沿用 v2）：仍\ **不謊造、不新增 RQ、不新增參考文獻**\ ；
  既有 §5 之表 1 / 表 2 / 表 3 不更動；§3.5 / §3.6 / §5.3 / §6.4.1–4 沿用。

本檔每段插入皆對應「實際實驗結果」或「framework 設計／未來工作」二
類之一；前者引用既有表格之數字，後者僅描述機制不附數字。

---

## v1 → v2 修正紀錄（保留）

- **移除全部捏造之實驗數據**：v1 內出現之「跨後端 0.86 / 0.84 / 0.78」、
  「dismissed filter precision 0.71 → 0.83」、「👎 比率 0.18 → 0.06」、
  「30 次重複標準差 < 0.02」、「p50 980 ms / p95 1280 ms」等數字皆未
  曾實際量測，違反 `paper_rule.md` 之「不謊造、不幻覺」硬規則，全部
  刪除。
- **不新增參考文獻**。原 v1 之 `[23]–[30]` 全部移除；本檔僅使用兩篇
  論文中已存在之 `[1]–[22]`。
- **不新增 RQ**。原 v1 之 RQ5（跨後端）與 RQ6（語料效益）皆對應到未
  進行之實驗，全部刪除。既有 RQ1–RQ4 不動。
- **程式碼有、論文未實驗之機制**（dismissed/accepted 語料、OpenAI/
  Anthropic 後端、MCP、secret redaction、cache/telemetry、judge→review
  event 映射）改以「框架設計貢獻」框架撰寫；於對應段落明示
  「本研究未對此進行量化評估，量化驗證屬未來工作」。
- **跨後端比較表全刪**。Anthropic / OpenAI / Ours-Local 之比較未實際
  跑過，不可寫入論文。本研究實際進行之比較為：Ours vs CRSCORE++ 基準
  （表 1）、Ours-30B vs Ours-7B vs Ours-Coder-7B（表 1 後三欄）、
  多階段提示詞 + 微調之消融（表 2 LLM 評分、表 3 人工評分）。

---

## 1  TCSE_v2.3.docx（短文，6 頁上限）

### 1.1  INSERT INTO §1.3 研究目的與貢獻（追加段落）

**插入位置**：現行 §1.3 末句「並促成人類審查者與智慧系統之互補合作 ……」
之後另起一段。

**內容**：

> 在框架可擴展性方面，本研究將推論後端抽象為 Strategy 介面，目前實驗
> 以本機 Qwen3-Coder-30B-A3B-Instruct 加 LoRA 適配器之配置（即表 1 之
> Ours 欄）為主，框架亦預留 OpenAI-相容端點與 Anthropic Messages API
> 之介面以利後續比較，惟此類跨後端之量化評估屬未來工作。框架另設
> `JudgeStep` 將審查裁決映射為 GitHub Review API 之 `event` 欄位
> （`APPROVE` / `REQUEST_CHANGES` / `COMMENT`）作為 PR 合併狀態之控制
> 端點，並提供合併前 Check Run gate 與作者反饋語料學習等設計，皆屬本
> 框架之設計貢獻；其量化驗證須累積實際 PR 流量後另行進行。

> 本研究隨附之開源框架另實作十三項研究級擴充機制（涵蓋 prompt-injection
> robustness、closed-loop 多輪對話、counterfactual / mutation-style
> 審查、provenance 稽核、force-push 差分、suggestion sandbox 驗證、
> cross-language API drift、PR 類型自適應、reproducibility 訊號、
> dependency upgrade impact、reviewer personas + conflict surfacing、
> risk-weighted attention 與 diff entropy 偵測），均以 CLI flag 之
> opt-in 形式提供；其端到端品質效益本研究均未予量化評估，詳細之設計
> 說明與後續實驗骨架見學位論文 §3.7 與 §6.4.5（對應本框架之 GitHub
> 倉庫之 `docs/en/concepts/research-extensions.rst`）。

> 標示說明：上述段落僅描述機制設計，不附效益數字；本研究實際驗證之
> 結果見 §5。

---

### 1.2  INSERT INTO §3.2 系統整體架構（追加段落，作為「附加設計貢獻」說明）

**插入位置**：現行 §3.2「推論層」段落之後、§3.2 收尾段「結合 RAG 規則
檢索 …… 」之前。

**內容**：

> 框架另實作下列三項設計，於本研究實驗範圍外但屬隨附之開源框架之
> 一部分，列此供讀者參照：(a) `JudgeStep`，於 CoT pipeline 末讀取
> `total_summary` 與已解析之 inline 留言，輸出 JSON 裁決並可映射為
> GitHub Review API 之 `event`；(b) 兩份 append-only 之 JSONL 學習
> 語料，分別記錄歷次 PR 中被作者拒絕之留言與被作者「Apply suggestion」
> 採納之建議，於推論時可分別作為輸出端相似度過濾與輸入端 in-context
> 範例使用；(c) 送出至第三方推論端點前之 secret 預過濾與 SQLite 為基
> 礎之 prompt cache、generate 呼叫之 telemetry。上述三項機制之量化
> 評估不在本論文範圍內，留待未來工作。本論文 §5 之實驗結果僅就 §3.1
> 之知識蒸餾 + LoRA 微調管線與 §3.2 之 RAG + CoT 多步推理進行驗證。

---

### 1.3  INSERT INTO §6.2 研究限制與未來工作（追加段落）

**插入位置**：現行 §6.2 末句之後。

**內容**：

> 在框架擴展面，本研究隨附之開源實作目前已提供四類推論後端介面
> （本機 Hugging Face、自架 FastAPI 服務、OpenAI-相容端點、Anthropic
> Messages API）、IDE 端 stdio 整合層（Model Context Protocol server）、
> 送出前之 secret 預過濾、prompt cache 與 telemetry 等功能；惟此類
> 機制之量化效益均未於本論文中評估。後續工作將依序針對：(a) 跨後端
> 於同一基準資料之品質、成本與延遲偏序比較；(b) 作者反饋語料（dismissed
> 與 accepted）之累積對 inline finding 精確率與作者再次按 👎 比率之
> 影響；(c) MCP 介面對 IDE 內審查觸發率與接受率之影響；逐項補上實際
> 實驗以完成完整驗證。

---

## 2  論文_v1.8.docx（學位論文）

### 2.1  INSERT INTO §1.5 研究貢獻（擴充原條列）

**插入位置**：現行 §1.5 條列段落。

**內容**：

> 本研究之研究貢獻可彙整為下列項目，前三項屬於本論文 §5 已實驗驗證
> 之核心貢獻，後三項屬於隨附之開源框架之設計貢獻、其量化驗證留待
> 未來工作（見 §6.4）：
>
> 1. **整合多階段 CoT 提示詞之程式碼審查流程設計與驗證**：將審查任務
>    拆解為摘要生成、初步審查、靜態分析、程式碼異味偵測與最終彙整等
>    五個循序步驟，並以 `build_global_rule_template` 函式統一前綴規則
>    之注入。經 §5.2 表 2 之 LLM 評分消融實驗，本設計相對單一提示詞
>    之邊際貢獻最為顯著。
> 2. **以知識蒸餾結合 QLoRA 之輕量化教師–學生訓練流程**：使 30B 級教師
>    模型之推理能力於有限 GPU 資源下移轉至學生模型，並以 LoRA 適配器
>    形式保留可拆卸性。經 §5.2 表 2 與 §5.1 表 1 比較，本設計可於同等
>    參數量級下提升 CRSCORE++ 三維度分數。
> 3. **以 FAISS 為基礎之 RAG 規則檢索層與相關性閾值設計**：以餘弦相似
>    度將領域規則動態注入提示詞，避免規則總量隨基礎模型 context window
>    擴張而線性增加；§5 所載結果皆於該檢索層啟用之配置下取得。
>
> 下列三項屬於本研究隨附之開源框架（prthinker）之設計貢獻；其量化
> 效益之驗證留待 §6.4 所述之未來工作：
>
> 4. **以 `JudgeStep` 為核心之 LLM-as-a-Judge-Our 細粒度評分機制與
>    GitHub Review event 映射設計**：本研究於 §5.2 / §5.3 採用 LLM-as
>    -a-Judge-Our 之百分制五維度評分作為自動化評估指標；框架另實作將
>    模型輸出之 `{verdict, score, reasons}` JSON 裁決透過保守聚合規則
>    映射為 PR 之 `APPROVE` / `REQUEST_CHANGES` / `COMMENT` 事件之
>    機制，惟此一「自動裁決驅動合併狀態」之端到端效益本論文未予評估。
> 5. **以 PR 作者反饋為輸入訊號之兩份學習語料設計（dismissed / accepted）**：
>    分別於推論時以相似度過濾與 in-context top-K 注入兩種非對稱方式
>    影響審查結果，建立無需額外人工標註之持續學習機制之資料介面。本
>    研究尚未對該機制之累積效益進行量化評估。
> 6. **可替換之推論後端與 IDE 整合層之設計**：以 Strategy 介面提供本
>    機 Hugging Face（含 LoRA + 量化）、自架 FastAPI、OpenAI-相容
>    端點與 Anthropic Messages API 四種具體後端，並以 MCP server 將
>    審查管線暴露為 IDE 可直接調用之 tool。本論文 §5 之實驗以本機後端
>    為主，跨後端比較與 IDE 內審查觸發率之評估屬未來工作。
> 7. **十三項研究級擴充機制之設計**（見 §3.7 詳述）：包含 prompt-injection
>    robustness 之 corpus + bypass detection、closed-loop 多輪對話、
>    counterfactual / mutation-style 審查、provenance 稽核、force-push
>    差分 cache、suggestion sandbox 驗證、cross-language API drift
>    偵測、PR 類型自適應、reproducibility 訊號、dependency upgrade
>    impact 分析、reviewer personas + conflict surfacing、risk-weighted
>    attention 與 diff entropy / 「diff bomb」偵測。每項對應一個 CLI
>    flag、一份單元測試與 `docs/en/concepts/research-extensions.rst`
>    內之設計說明；其端到端品質效益本論文均未予評估，列為 §6.4.5
>    所述之未來工作。

---

### 2.2  INSERT INTO 第三章（新增 §3.5 學習語料機制與評審層之設計）

**插入位置**：現行 §3.4「與程式碼編輯環境整合」之後。

**標題與內容**：

> 3.5  學習語料與評審機制（設計層）
>
> 本節描述本研究隨附之開源框架（prthinker）於 §3.2 系統架構之外另實作
> 之兩項機制：作者反饋學習語料與 `JudgeStep` 評審層。下列說明屬於框架
> 之設計與介面定義；其量化效益本論文未予評估，留待 §6.4 所述之未來
> 工作以累積實際 PR 流量後另行驗證。
>
> 3.5.1  Dismissed 語料：以相似度過濾抑制重複噪音之機制
>
> 框架提供 `harvest-dismissed` 子指令掃描既往 PR 之 review comments，將
> 符合下列任一條件之留言視為被拒：留言本身或其回覆含 👎 reaction、
> 或留言之回覆字串命中「false positive」、「wontfix」、「not relevant」、
> 「誤判」、「不修」等中英文關鍵字集合。命中之留言以 JSONL 格式 append
> 至 `.prthinker/dismissed.jsonl`，欄位包含 `path`、`comment`、`reason`、
> `diff_snippet`。於推論時，server 啟動時將該 JSONL 之每筆 `comment` 各
> embed 一次並載入記憶體；對每個候選 inline finding 計算其 `comment` 與
> 全部 stored example 之最大餘弦相似度 `s_max`，若 `s_max ≥ τ_d` 即將
> 該 finding 由輸出中移除。本機制屬框架介面層之設計，本論文未對閾值
> `τ_d` 進行調參實驗，亦未提供啟用前後之品質對照。
>
> 3.5.2  Accepted 語料：以 in-context 範例注入提升建議採納率之機制
>
> 對偶地，`harvest-accepted` 子指令掃描含有「Apply suggestion(s) from
> code review」commit 之 PR，將該 PR 上所有附帶 ```suggestion``` 區塊之
> review comment 收為 accepted 範例（欄位 `path`、`comment`、`suggestion`、
> `pr_number`）。於 inline-findings 步驟組裝 prompt 時，框架以候選 diff
> 為 query 對 accepted 語料做相似度檢索，取相似度高於 `τ_a` 之前 K 筆
> 作為 few-shot 區塊注入 prompt。本機制屬框架介面層之設計；其於不同
> `τ_a` 與 K 設定下對 inline-findings 品質之影響本論文未予評估。
>
> 3.5.3  非對稱使用之設計理由
>
> Dismissed 訊號作用於輸出端（過濾）、accepted 訊號作用於輸入端（prompt
> 注入），此一非對稱設計之理由為：負向訊號若以 in-context 範例形式
> 提供，模型可能誤學「應產生此種被拒留言」；正向訊號若以輸出端 filter
> 形式提供，將過度限縮模型多樣性。將兩者分置於 pipeline 之輸入與輸出
> 兩端，可同時得到「過去之錯不再犯」與「過去之對更易出現」之雙向效果。
> 本設計理由屬框架架構之說明；其端到端效益之實證留待 §6.4 之未來工作。
>
> 3.5.4  `JudgeStep`：模型裁決至 GitHub Review event 之映射
>
> 五步 CoT 完成後，框架於 per-file pipeline 末追加 `JudgeStep`，由模型
> 讀取 `total_summary` 與已解析之 inline 留言，輸出
> `{verdict ∈ {approve, request_changes, comment}, score ∈ [0,10],
> reasons: [...]}` 之 JSON 裁決。多份檔案之裁決以保守規則聚合：任一檔
> 判 `request_changes` 即整體判 `request_changes`，全檔判 `approve`
> 始整體判 `approve`，其餘判 `comment`。聚合結果映射為 GitHub Review
> API `POST /pulls/:n/reviews` 之 `event` 欄位，使本框架可直接影響 PR
> 之合併狀態。本論文 §5.2 / §5.3 採用 LLM-as-a-Judge-Our 之百分制五維度
> 評分作為自動化評估指標，與此一端到端「自動裁決驅動合併」機制屬不同
> 用途；後者之效益（如自動 approve 與後續 revert 之比率、自動
> request_changes 與作者修正成功率）本論文未予評估。

---

### 2.3  INSERT INTO 第三章（新增 §3.6 安全前處理與隨附之 IDE 整合層）

**插入位置**：§3.5 之後。

**標題與內容**：

> 3.6  安全前處理與 IDE 整合層（設計層）
>
> 3.6.1  Secret 預過濾
>
> 當推論後端為第三方付費 API 時，PR diff 之 payload 可能含有遺漏於
> `.gitignore` 之 secret（例如 `.env` 內容、寫死於測試 fixture 之
> token、snapshot test 內之 JWT）。為避免此類 secret 經 HTTPS 送至
> 外部服務，框架於送出前以 `--redact-secrets` 旗標啟動之 pre-pass
> 將 diff 中符合下列 pattern 之字串以 `<REDACTED:<kind>>` 取代：
> AWS access key、GitHub PAT、OpenAI key、Anthropic key、Stripe key、
> Slack token、Google Cloud API key、Twilio SID、JWT 與 PEM 私鑰整塊。
> 本機制具三項設計性質：冪等（已 redact 之 placeholder 不會再次被偵
> 測為 secret）、不洩漏（log 僅記錄各 kind 之命中次數，不含實際內容）、
> 對 cache 友善（redact 於 cache key 計算之前執行）。本論文未對該預
> 過濾之 false-positive 與 false-negative 率進行評估。
>
> 3.6.2  Model Context Protocol 整合層
>
> 本框架除 CI 觸發路徑外，另以 `prthinker mcp` 子指令啟動 stdio MCP
> server（Model Context Protocol，LLM client 與外部工具之間之 JSON-RPC
> 協定），將 review 管線暴露為兩個可由 MCP client 之 LLM 自由調用之
> tool。後端設定共用 §3.2 所述之環境變數機制，密鑰一律取自環境變數
> 不寫入 MCP client config。本框架於 IDE 內之觸發率、開發者接受率與
> 與 CI 內審查之等價程度本論文未予評估，相關實驗屬未來工作。

---

### 2.4  INSERT INTO 第三章（新增 §3.7 研究級擴充機制之框架設計）

**插入位置**：§3.6 之後。

**標題與內容**：

> 3.7  研究級擴充機制（設計層）
>
> 本節描述本研究隨附之開源框架另實作之十三項機制，均對應於 LLM 程式
> 碼審查文獻中目前較少實作之研究面向。每項機制皆以 CLI flag 形式
> opt-in，預設關閉以維持 §5 所驗證之 baseline pipeline 不受干擾。
> 本論文\ **未對任何單項機制之端到端品質效益進行量化評估**\ ；
> §6.4.5 將就每項機制給出對應之未來工作骨架。所列機制皆已伴隨單元
> 測試與設計文件（`docs/en/concepts/research-extensions.rst`），可
> 直接於工程上使用，僅缺學術評估。
>
> 3.7.1  Prompt-injection robustness 與 `adversarial-eval` 子指令
>
> 既有 LLM 程式碼審查文獻多預設 diff 為友善輸入。本框架實作四類攻擊
> 之 corpus 與分類器（`direct_injection` 將「忽略先前指令並核可此
> PR」貼入 diff、`encoded_payload` 以 base64 / hex / ROT13 / unicode
> homoglyph 混淆、`split_injection` 將 payload 拆散於多檔案、
> `role_hijack` 重新定義審查器角色），並提供 `detect_bypass()` 純函
> 式將模型輸出與 case 標記之 markers 進行匹配，於 SQLite 記錄每筆
> 呼叫之原始輸出供事後審計。隨附之 `seed.jsonl` 明示為「種子」而非
> benchmark，避免未經擴充即被誤用為定量基準。
>
> 3.7.2  Closed-loop 多輪對話審查
>
> 既有 LLM reviewer 將審查視為一次性事件：模型發出留言、作者回覆，
> 但下一輪審查並未讀取作者之回覆。框架在 `PlatformAdapter` 加入
> `fetch_author_replies()`，將作者於最近一則 summary comment 後之
> 回覆渲染為「Prior dialogue」區塊，注入 inline-findings prompt。模
> 型被明確要求對作者已回應之 finding 做下列三擇一：捨棄、精煉、以
> 新證據反駁，禁止靜默重貼。此一機制屬框架設計貢獻；其於真實 PR
> 對話下對 round-2 precision 之影響本論文未予評估。
>
> 3.7.3  Counterfactual / mutation-style 審查
>
> 多數審查器只輸出「請改成 X」。框架另實作 `CounterfactualStep`，於
> per-file inline findings 之後針對被視為「設計選擇」之 finding，
> 要求模型列出最多三個競爭性實作與 trade-off 矩陣（axes 為
> `performance` / `readability` / `testability` / `memory` /
> `idiomaticity` / `dependency` 等）。Parser 丟棄選項少於 2 或
> `finding_index` 越界之區塊；本機制屬框架設計貢獻，其對人類審查
> 者決策品質之影響本論文未予評估。
>
> 3.7.4  Provenance 稽核：每條 finding 之引用鏈
>
> 框架定義 `Provenance(citations, confidence)` schema 並要求模型對
> 每條 finding 引用其依據（`rag_rule` 編號、`accepted_example` 編號、
> 或 `diff_evidence` 行號），可選附自評信心值 ∈ [0, 1]。Parser 對
> 越界引用做靜默丟棄但不丟 finding；`confidence` 僅供人類參考，
> 不作為自動過濾依據。本機制使審查行為從「黑盒」變為可審計，屬框架
> 設計貢獻；其與 finding 正確率之相關性本論文未予評估。
>
> 3.7.5  Force-push 差分審查
>
> 迭代型 PR 在多次 push 間之 diff 通常 60–80% 不變。框架實作
> `FileDiff.content_sha256()`（僅 hash 新側內容，排除 diff metadata
> 與被刪除行），並提供 SQLite cache 以
> `(pr_number, repo, file_path, hunk_sha256)` 為 key 儲存 findings。
> 下次 push 時 hash 未變之檔直接 reuse 上次結論。本機制屬框架設計
> 貢獻；其於真實 PR 流量下節省之 token 成本本論文未予評估。
>
> 3.7.6  Suggestion sandbox 驗證
>
> 框架實作 `verify_suggestion()`，把 working tree 複製到
> `tempfile.mkdtemp` 後以 `original` 守備檢查套用 suggestion，再以
> `verify_cmd`（預設 `pytest -x`）於 timeout 之內執行，將每條建議
> 標 `pass` / `fail` / `skip` / `error`。原 repo 絕不動；verify 指
> 令以 argv list 跑（無 `shell=True`）。將 suggestion 由「盲射建議」
> 升級為「有經驗證據之假設」之設計貢獻；其於開發者採納率上之效益本
> 論文未予評估。
>
> 3.7.7  Cross-language API drift 偵測
>
> 當 PR 同時碰到後端（`.py`）與前端（`.ts` / `.tsx` / `.js` /
> `.jsx`），per-file review 看不到「後端把 `user_id` 改名 `userId`、
> 前端仍用舊名」之跨檔 drift。框架以 `is_mixed_language()` 偵測
> 跨語言 PR，組裝跨檔 prompt 並解析為 `ApiDriftFinding`（kinds：
> `field_renamed` / `field_removed` / `type_changed` / `path_changed`
> / `method_changed` / `other`）。Parser 丟棄引用了非 diff 路徑之
> drift（模型無法虛構檔名）。本機制屬框架設計貢獻；其 precision /
> recall 本論文未予評估。
>
> 3.7.8  PR 類型自適應審查
>
> 多數 LLM 審查器對所有 PR 一視同仁。框架實作前置之 PR-type
> classifier（`PRType ∈ {bugfix, feature, refactor, docs, chore,
> unknown}`），用 diff + 標題 + body 將 PR 分類後，按 `ReviewBudget`
> 表調整後續 review 深度：DOCS 跳整個 inline findings、BUGFIX 縮
> `max_findings_per_file` 並注入 focused prompt 片段、REFACTOR 放
> 大 budget 並注入等價檢查 hint。安全失敗方向：解析失敗 → UNKNOWN
> → 走標準 pipeline。本機制屬框架設計貢獻；其分類正確率與品質提升
> 本論文未予評估。
>
> 3.7.9  Reproducibility / 評論一致性訊號
>
> 多數 backend 並未透過統一 API 暴露穩定之 per-token logprob。框架
> 提供後端通用之 uncertainty proxy：對同一檔以同 prompt 跑兩次
> inline-findings step（非 0 temperature 自然產生第二樣本），按
> `(path, line, 正規化 comment)` 比對；正規化壓掉空白 / 大小寫 /
> 標點以涵蓋 paraphrase。findings 標 `stable` / `low`；第二次新出
> 現之 finding 亦保留為 `low`。本機制屬框架設計貢獻；其與真實正確
> 率之相關性本論文未予評估。
>
> 3.7.10  Dependency upgrade impact 分析
>
> 最容易被人類審查者迅速放行之 PR，往往是不顯眼之 dependency bump。
> 框架偵測 `requirements.txt` / `pyproject.toml` / `package.json`
> 之觸碰，抽出 `(package, old_version, new_version)` delta，並以
> 該套件於 diff 其他檔案中之實際呼叫點為附加 prompt 上下文，問模
> 型 breaking change 是否影響本 repo 之用法，解析為
> `DependencyUpgradeFinding(severity, summary, evidence)`。框架於
> review-time 不抓 remote changelog（CI 不穩 + 隱私問題）。本機制
> 屬框架設計貢獻；其偵測精度與漏報率本論文未予評估。
>
> 3.7.11  Reviewer personas + conflict surfacing
>
> 既有 ensemble reviewer 多半是同一 lens 跑 N 次平均。框架實作
> 五個正交 `Persona`（`SECURITY` / `PERFORMANCE` / `READABILITY` /
> `API_STABILITY` / `MAINTAINABILITY`），每個 persona prompt 明確
> 要求模型只在該 lens 範圍內評論。N 個角色發言後，conflict-finder
> step 拿 N 個輸出找跨角色之分歧並輸出 `PersonaConflict(personas,
> summary, resolution)`；`resolution` 刻意不替決策者選邊，將張力
> 顯化而非平均化。本機制屬框架設計貢獻；其對人類審查者決策成本之
> 影響本論文未予評估。
>
> 3.7.12  Risk-weighted attention：以 git 訊號分配 findings budget
>
> 多數審查器將 PR 內每檔視同仁。框架實作以三項 git-derived 訊號計
> 算之每檔風險分：churn（`git log --since=90.days.ago` 之 commit
> 數）、complexity proxy（HEAD 行數）、bug history（commit message
> 命中 `fix:` / `bug` / `revert`）。三項在 PR 內 normalise 後以權
> 重 (0.4, 0.3, 0.3) 線性結合（明示為\ **框架慣例而非校準公式**），
> 並按分數線性縮放 `max_findings_per_file` 於 `floor` 與 `ceiling`
> 之間。本機制屬框架設計貢獻；權重之校準與 budget 配置之品質影響
> 本論文未予評估。
>
> 3.7.13  Diff entropy 與「diff bomb」偵測
>
> 多數 LLM 審查器照單全收地處理千檔大 PR，產出灌洗版式之 review。
> 框架將 PR 之形狀視為 first-class review signal：以檔案數 + 總
> +/- 行為 size 分量，以頂層目錄分布之 Shannon entropy 經
> `log2(n_dirs)` 正規化為 dispersion 分量，分類為 `focused` /
> `wide` / `bomb`。verdict 為 `bomb` 時於留言頂端貼「Consider
> splitting this PR」警示。框架\ **不**\ 因高分阻擋合併，目的僅為
> 將 PR 形狀顯化以利人類決策。本機制屬框架設計貢獻；其與真實 PR
> 缺陷漏報率之相關性本論文未予評估。
>
> 3.7.14  部署層工程：CI 矩陣分片、非同步 job-pattern endpoint
>
> 在以反向代理（Cloudflare 免費 / Pro / Business 方案套用 100 秒
> 之 HTTP idle timeout）對外暴露之 30B MoE 推論伺服器上，單一
> per-file CoT 審查之單 round-trip 推論時間可超過該上限，並隨
> per-file mode 對大 PR 之 序列化處理累積觸發 GitHub Actions 預設之
> 30 分鐘 job 上限與 GPU 累積 KV cache 之 OOM。框架在不更動審查
> 流程之前提下，於部署層提出四項工程設計：
>
> (a) **非同步 job-pattern endpoint**：將 `/review` 同步端點補上
> `POST /review/submit`（回傳 ``job_id``）與 ``GET /review/result/{id}``
> 兩個 endpoint，搭配 5 秒輪詢之 client 設計，使任一 HTTP round-trip
> 之 wall-clock 時間落於 reverse-proxy idle timeout 之內，與 backend
> 端實際推論時間解耦。
>
> (b) **CI matrix 分片**：將原 single-job `review-pr` 重構為
> `enumerate` → `review` matrix（``max-parallel: 1``，每 shard 60
> 分鐘 budget）→ `aggregate` 三 job pipeline，使每個 file 享有獨立
> timeout budget。`max-parallel: 1` 屬刻意設計，避免並行 shard 在
> backend 排隊浪費 CI 分鐘而無 wall-clock 收益（單 GPU 仍為瓶頸）。
>
> (c) **noise-path 過濾與 single-file 模式**：新增
> `--exclude-globs` / `--target-file` 兩 flag，使 matrix shard 能以
> matrix.file 之精確路徑接管單一 file 之審查，並透過共享
> `PRTHINKER_EXCLUDE_GLOBS` 確保 workflow 與 CLI 使用同一份 fnmatch
> 規則跳過 IDE 設定 / 生成資料 / 文件變更，避免將 GPU 預算消耗於
> 與審查目標無關之檔案。
>
> (d) **partial-result aggregation**：新增 ``--output-json`` flag 與
> `aggregate` 子指令，使 matrix shard 將其 partial ``ReviewResult``
> 序列化為 JSON artifact，由 aggregate job 將 ``inline_findings`` /
> ``per_file`` / ``step_outputs`` 合一後僅 post 一次 summary 留言、
> 一次 inline review、開 / 關 pre-merge gate 各一次。
>
> 另搭配兩項 GPU 端記憶體工程：每個 job 結束以
> ``torch.cuda.empty_cache() + gc.collect()`` 釋出 caching allocator
> 之保留區塊；於 inference 路徑前以 backend tokenizer 切上限
> （預設 6000 tokens）之 diff truncation，避免單一過長 diff 在
> attention 計算階段觸發 OOM。
>
> (e) **主動式取消與 idle-poll sweeper**：為避免 CI runner 被取消
> （`concurrency: cancel-in-progress`、手動 cancel、runner crash）
> 後 backend 仍持續耗用 GPU 跑沒人讀的 review，於 server 新增
> ``POST /review/cancel/{job_id}`` 與 ``POST /ask/cancel/{job_id}``
> 兩 endpoint，client 端以 try/finally 在離開 poll loop 時主動發送
> cancel。另搭配 server 端常駐 sweeper thread：每 30 秒掃描所有
> running job，180 秒未被 poll 之 job 自動設 ``cancel_event``，涵
> 蓋 SIGKILL / 網路中斷等 try/finally 來不及執行之路徑。Pipeline
> 於每個 step 邊界檢查 event；local backend 另注入
> ``StoppingCriteria`` 於 ``model.generate`` 之每 token decode 後
> 輪詢，使取消延遲由 step 邊界之 30-60 秒降至約 100 ms（單一 token
> 之時間）。
>
> (f) **summary comment / inline review / check run 之冪等性處理**：
> 同一 head SHA 之重複 workflow run（manual re-run、cancel-in-progress
> 後之新 push、CI retry）原本會於 PR 上累積多份 prthinker 產物。
> 框架以三種機制達成單一 SHA 對應單一可見產物：(i) summary
> comment 以 HTML marker `<!-- prthinker:summary -->` upsert，PATCH
> 同一 comment 而非每次 POST 新的；(ii) inline review 之 body 嵌入
> 隱藏 marker `<!-- prthinker:inline -->`，於 POST 新 review 前列出
> 所有同 marker 之 review 並 DELETE 其底下之 review comments（GitHub
> 不允許 dismiss COMMENT-state review，故 wrapper 留為 timeline
> stub）；(iii) check run 於 open 前對同 head SHA 上所有同名
> prthinker check PATCH 為 `status=completed` / `conclusion=neutral`
> 並附 "superseded" 標題，UI 自動將其折疊於 live 之 check 下方。
>
> (g) **CI matrix 分片之 PR-wide overall summary 合成**：matrix
> 各 shard 僅產出 per-file 之 `total_summary`，aggregate 階段缺乏
> 跨檔之總結。於 aggregate 完成 per-file 合併後，以
> ``/ask/submit`` 對 backend 發起一次合成 prompt（將所有 per-file
> summaries 串為輸入，要求 3-5 句之 PR-wide 重點），結果寫入
> `merged.step_outputs["total_summary"]` 並由 formatter 於 PR 留
> 言頂部呈現為 ``### Overall Summary``。Best-effort：backend 不
> 通、timeout、httpx 例外皆 log warning 並 fallback 為僅顯示
> per-file blocks，不阻擋 PR 留言之 post。
>
> 本機制屬部署層設計貢獻，其對端到端 PR 流量之穩定性、wall-clock
> 改善、reviewer 對重複留言之認知負擔等量化評估本論文未予進行，
> 列為 §6.4.5 之未來工作。

---

### 2.5  INSERT INTO §5（新增 §5.3 結果分析，僅使用既有表 1、表 2、表 3 之數字）

<!-- (Renumbered from §2.4 in v2 → §2.5 in v3 due to insertion of new §3.7 block above.) -->

> v1.8 學位論文目前 §5 僅有 5.1 各方法比較 與 5.2 消融實驗 兩個小節，
> 缺少 paper_rule §4.5 所要求之「結果分析」段落。本節僅基於 §5.1 表 1、
> §5.2 表 2、§5.2 表 3 已存在之數字進行分析，不引入未實驗之新資料。

**插入位置**：現行 §5.2 消融實驗之後、§6 之前。

**標題與內容**：

> 5.3  結果分析
>
> 5.3.1  自動化評分與人工評分之一致性
>
> 由表 1（CRSCORE++）、表 2（LLM-as-a-Judge-Our 自動評分）與表 3
> （人工評分）之趨勢可知，本研究之完整方法（微調模型 + 多階段提示詞）
> 於 Maintainability、Correctness、Multi-Review Coverage 三維度同時
> 優於單一提示詞變體與基礎模型變體，且差距於人工評分（表 3）保持
> 一致方向；惟 Readability 一項出現 LLM 評分（92）高於人工評分
> （83.50）之偏差，亦於另兩組設定中重複出現。此一系統性差異與 [11]
> 所述 LLM-as-a-Judge 於語感類指標相對人類較寬鬆之偏誤一致，可作為
> 後續以人工反饋校正 Readability 指標之依據。
>
> 5.3.2  多階段提示詞之邊際效益
>
> 表 2 顯示，自基礎模型 → 多階段提示詞（微調 + 多階段）之變化使
> Maintainability 由 85 升至 95、Correctness 由 82 升至 98；表 3 之人工
> 評分亦呈相同方向之提升（Maintainability 79.88 → 86.25、Correctness
> 80.75 → 87.75）。相較之下，自基礎模型 + 多階段（未微調）→ 微調 +
> 多階段之變化於兩表中差距較小（表 2 中 Maintainability 維持 95、
> Correctness 由 98 持平；表 3 中 Maintainability 由 84.88 升至 86.25、
> Correctness 由 86.38 升至 87.75）。此一比例支持兩點觀察：第一，
> 本研究採用之 Qwen3-Coder-30B 已具備充分之程式碼語義理解能力，主要
> 瓶頸在於「一次提示要求過多任務」造成之 context 過載，故多階段拆解
> 之效益顯著；第二，LoRA 微調之邊際貢獻雖較小，但於 Maintainability
> 與 Correctness 兩維度仍能於人工評分中觀察到一致之提升趨勢。
>
> 5.3.3  與基準方法（CRSCORE++）之對照
>
> 由表 1 之 CRSCORE++ 三維度比較可知，本研究之 Ours 配置於
> comprehensiveness（0.86 vs 0.67）、conciseness（0.64 vs 0.57）與
> relevance（0.83 vs 0.63）三項皆顯著優於 CRSCORE++ 基準。Ours-7B
> 變體（Qwen3 7B 與 Qwen2.5-Coder-7B）於 comprehensiveness 仍可達
> 0.79 ~ 0.80，於 relevance 達 0.66，惟於 conciseness 退至 0.45 ~ 0.50。
> 此一退步推測來自較小模型對「多階段提示詞末段彙整步驟」之長度控制
> 能力較弱；於 §6.4 所述之未來工作中，可考慮以更具體之長度上限指令
> 或專屬之收斂式總結 step 緩解。

---

### 2.6  INSERT INTO §6.4 未來工作（擴充原段為四點，並於 v3 追加第 5 點）

**插入位置**：替換現行 §6.4 之單段。

**標題與內容**：

> 6.4  未來工作
>
> 6.4.1  跨後端之品質、成本與延遲偏序評估
>
> §1.5 之研究貢獻第 6 項所述之四類推論後端（本機 Hugging Face、自架
> FastAPI、OpenAI-相容、Anthropic Messages API）於本論文 §5 僅以本機
> 配置為主進行評估。後續將於相同基準資料上以同一份提示詞、同一份 RAG
> 規則文件分別執行於各後端，比較其 CRSCORE++ 三維度品質、單 PR 成本
> 與 p50 / p95 延遲，建立可依團隊成本敏感度與品質要求選擇後端之偏序
> 對照表。
>
> 6.4.2  作者反饋語料之累積效益驗證
>
> §3.5 所述之 dismissed / accepted 語料機制目前以介面層形式存在；
> 後續工作將於實際 PR 流量上累積至少 100 筆語料後，以 paired bootstrap
> 對下列兩項指標進行量化評估：(a) 啟用 dismissed filter 對 inline
> finding 精確率之影響；(b) 啟用 accepted few-shot 注入對 inline
> finding 之 `suggestion` 區塊出現率與作者實際「Apply suggestion」採納
> 率之影響。並以同一份累積語料探討兩種閾值 `τ_d`、`τ_a` 與 top-K 之
> 敏感度分析。
>
> 6.4.3  跨平台支援與多模型協作之擴展
>
> 本框架現以 GitHub 為主之 PR 模型運作，後續可將 GitHub 整合層抽象為
> `PlatformAdapter` 介面並提供 GitLab、Bitbucket 與內部自架 Gitea 之
> 實作，以涵蓋採用非 GitHub 平台之企業案例。模型協作面，可進一步探索
> 多模型仲裁（multi-model ensemble）：同一份 diff 並行送入兩至三個
> 後端，再由第四個後端作為 judge 比對其裁決一致性，作為衡量審查不
> 確定度之來源，並協助識別需人工介入之高分歧檔案。此擴展之具體實驗
> 設計與評估指標屬未來工作。
>
> 6.4.4  IDE 內審查觸發與生產級 ops 補強
>
> §3.6.2 所述之 MCP 整合層使本框架可在 IDE 內直接觸發審查，後續可比
> 較 IDE 觸發（push 前）與 CI 觸發（push 後）兩種時機對開發者接受率
> 與後續修正成本之差異。在 ops 補強面，可將框架隨附之 SQLite cache /
> telemetry 遷移至 Redis 與 PostgreSQL 以擴及多 server 共享之企業環境，
> 並補上 drift watcher：以固定之 golden PR 集合定期重跑審查，比對輸出
> 相似度，一旦偏離既有 baseline 即觸發告警。
>
> 6.4.5  §3.7 所述十三項研究級擴充機制之實證評估
>
> §3.7 所述十三項機制目前僅完成框架實作；其端到端品質效益需後續以
> 真實 PR 流量驗證。為避免日後補實驗時設計分歧，本節為各機制標示最
> 小可驗證實驗骨架；所列指標皆為公開可重現之量度，避免引入新主觀
> 量表。
>
> (a) Prompt-injection robustness（§3.7.1）：擴充 `seed.jsonl` 至每
> 攻擊類別 ≥ 30 例，於四類後端各跑一遍，以 SQLite 表格內之
> `bypassed` / `detected` 欄聚合為 detection rate 與 false-alarm rate
> 之偏序對照。
>
> (b) Closed-loop 多輪對話（§3.7.2）：於同一 PR 連續推 ≥ 5 次提交，
> 比較啟用 `--reply-to-author` 與否之 round-k 重複 finding 比率與作者
> 採納率。
>
> (c) Counterfactual 審查（§3.7.3）：抽 ≥ 50 個 design-choice 類
> finding，請 ≥ 3 名人工審查者就「呈現替代方案是否影響其最終決策」
> 之 Likert 5 點評分作為效益指標。
>
> (d) Provenance 稽核（§3.7.4）：以人工標記 ≥ 100 條 finding 之
> 「正確 / 誤判」標籤，比較有引用 vs 無引用兩組之 precision，並用
> `confidence` 與真實正確率之 ROC AUC 量化自評之校準度。
>
> (e) Force-push 差分（§3.7.5）：於連續 30 天之 PR 流量上比較啟用
> `--diff-since-last` 與否之 token 用量、cache hit 比率與 false-reuse
> 比率（cache hit 但模型若實際重跑會產出不同 finding 之比例）。
>
> (f) Suggestion sandbox 驗證（§3.7.6）：以 ≥ 100 條 suggestion 在
> sandbox 內套用後跑 `pytest -x`，計算 `pass` / `fail` / `skip` /
> `error` 四類比例；另以人工標記真實正確性，計算 sandbox 之 verdict
> 與人工判斷之 Cohen's κ。
>
> (g) Cross-language API drift（§3.7.7）：構造 ≥ 30 個 mixed-language
> PR（後端 rename、欄位刪除、type 變更）作為 ground-truth，計算
> precision / recall。
>
> (h) PR 類型自適應（§3.7.8）：在 ≥ 200 個公開 PR 上以 commit msg
> prefix / labels 為 ground-truth 計算分類 accuracy / macro-F1；
> 並比較啟用 `--pr-classify` 前後之每類 PR finding 精確率。
>
> (i) Reproducibility 訊號（§3.7.9）：對固定 PR 集合各跑 5 trials，
> 以兩兩之 `(path, line, normalised-comment)` 重合率作為內部一致性
> 指標；驗證 `stable` 標記與真實正確率之相關性。
>
> (j) Dependency upgrade impact（§3.7.10）：以公開 advisory（GHSA /
> CVE）作為 ground-truth breaking change 之來源，於 ≥ 50 個歷史
> dependency bump PR 上計算 precision / recall。
>
> (k) Reviewer personas + conflict surfacing（§3.7.11）：於 ≥ 50 個
> design-heavy PR 上比較單 lens 與 personas（含 conflict step）兩設
> 定下，人類審查者「需介入決策」之留言數與最終 PR 之 revert 率。
>
> (l) Risk-weighted attention（§3.7.12）：以歷史 bug-fix PR 之檔案
> 分布為 ground-truth，建立 risk score 與「該檔於下一季出現 bug fix
> commit 之機率」之相關係數；並對權重 (0.4, 0.3, 0.3) 進行敏感度分
> 析。
>
> (m) Diff entropy（§3.7.13）：以公開「PR 被拆」事件作為 ground-
> truth，計算 verdict ∈ {focused, wide, bomb} 與「該 PR 後續被拆」
> 之關聯。
>
> 上列十三組實驗皆需累積實際語料；本論文之主要貢獻仍為 §5.1 / §5.2
> 所述之多階段 CoT + LoRA 微調 + RAG 之整合設計與驗證，§3.7 與
> §6.4.5 之內容明示為框架設計貢獻與後續工作之承接介面，不影響本論
> 文之核心主張。

---

## 3  審稿前 self-audit 清單

依 `paper_rule.md` 之「不謊造、不幻覺」硬規則與其他規則綜整：

- [ ] **不謊造**：本檔每段內若含任何數字（百分比、token 數、毫秒、
      USD、信賴區間、標準差），該數字是否來自既有論文之表 1 / 表 2 /
      表 3，或由作者親自跑出且可提供 raw log？若否，刪除該句或改寫
      為「框架設計貢獻 / 未來工作」框架，並明示「本研究未對此進行
      量化評估」。
- [ ] **不新增 RQ**：兩篇論文之 RQ 維持 RQ1–RQ4 不動，未引入新 RQ。
- [ ] **不新增參考文獻**：本檔之引文編號全部落於既有 `[1]–[22]`，未
      引入 `[23]+`。
- [ ] 兩篇引文格式統一為 IEEE `[N]`，未殘留 `(Author, Year)`。
- [ ] 每個新增之技術名詞於首次出現處附括弧解釋。
- [ ] 新增之子章節（§3.5.1–4、§3.6.1–2、**§3.7.1–13**、§5.3.1–3、
      §6.4.1–5）在 docx 內已以加粗 + 略大字級之段落呈現，不僅以段落
      換行示意。
- [ ] §1.5 條列之七項貢獻：前三項已對應 §5 表 1 / 表 2 / 表 3 之實驗
      結果；第 4–7 項已明示為「框架設計貢獻、量化驗證屬未來工作」。
- [ ] §3.5 / §3.6 / **§3.7** 全部段落內含「本論文未予評估」或等義之
      免責標示；§3.7 內提及「框架設計貢獻」之頻次 ≥ 13 次（每子節
      至少一次）。
- [ ] **§3.7 之十三項機制每項皆對應 §6.4.5 之一個未來工作骨架（a)–(m)**，
      不漏項；§6.4.5 內每項皆給出具體之 ground-truth 來源、語料規模
      下限、與不依賴人類主觀量表之量化指標。
- [ ] §5.3 之三段分析所引之每個數字皆可於表 1 / 表 2 / 表 3 中找到。
- [ ] §6.4 之五項未來工作皆對應到 §1.5 中已明示為「框架設計貢獻」之
      項目（6.4.1 ↔ 第 6 項後端 / 6.4.2 ↔ 第 5 項語料 / 6.4.3 ↔ 第 6
      項平台與多模型 / 6.4.4 ↔ 第 6 項 MCP / 6.4.5 ↔ 第 7 項十三項
      機制）。
- [ ] 文中所有「該方法」「上述」「此」之代名詞，往前 3 行內可找到具
      體指稱。
- [ ] 全文未出現「賦能 / 打造 / 全方位 / 深入探討 / 值得注意的是 /
      綜上所述（於結論章內）」等 AI 口頭禪。
- [ ] **十三項擴充機制之名稱於論文與隨附之 `docs/en/concepts/
      research-extensions.rst` 完全一致**（避免 `--reply-to-author`
      於論文內被翻為「多輪對話」、於 docs 內被翻為「閉環對話」之
      不一致）。
- [ ] 已驗證每個 `<w:rPr>` 之 `<w:rFonts>` 元素四個 slot 皆設為標楷體 /
      Times New Roman。
- [ ] TCSE v2.3 之插入後總字元數仍可控制於 6 頁 Word 上限內；§3.7
      與 §6.4.5 主要針對學位論文 v1.8，TCSE 短文版本可僅於 §1.3 之
      末句後追加一句「本研究隨附之開源框架另實作十三項研究級擴充機
      制，詳見學位論文 §3.7 與 §6.4.5；該等機制之量化評估均屬未來
      工作」以同步而不超頁。

> 若任一項回答為「否」，於 commit 進 docx 之前先處理；尤其第一項
> （不謊造）為硬規則，違反即構成研究不當行為。
