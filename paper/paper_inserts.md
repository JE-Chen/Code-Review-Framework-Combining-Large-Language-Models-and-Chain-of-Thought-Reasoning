<!-- markdownlint-disable-file MD029 -->
<!-- Ordered-list numbering follows the paper's §1.5 / §3.7 / §6.4.5
     contribution numbering (items 4-7 continue 1-3 across a paragraph
     break, 3.7.14 sub-items run (a)-(p), 6.4.5 sub-items run (a)-(q)).
     Reformatting them to restart at 1 would lose the cross-section
     numbering that the paper itself uses. -->

# 論文補充內容（drop-in 段落集 — v3.4 修正版）

## 修正聲明

本版相對於 v3.3 之關鍵差異（v3.4）：

- **新增 §3.7.22 審查導覽與分流輔助**：對應隨附框架近期之 reviewer
  orientation 整合。其中唯一使用推論者為\ **模型生成之逐檔變更走查**\
  （``--walkthrough``）──於 per-file 管線新增一個 ``WalkthroughStep``，
  產出二至四句「此變更做了什麼、為何」之敘事，釘於該檔區塊最上方，作為
  既有\ **無推論**\ 之 commit-message PR 概覽（§3.7.20 之 ``pr_overview``）
  之推論側對應物。其餘導覽／分流輔助皆為 runner-safe 純轉換：inline 留言之
  Conventional Comments 標籤、跨檔 Top-findings 佇列、Must-fix 之原始碼行
  引用、每檔變更規模徽章、建議審閱順序（``--review-order``）、變更地圖
  （``--change-map``）、缺測試啟發式提示、high-risk 檔案註記與 reviewer
  checklist。皆隨附單元測試；\ **不計入 §3.7 之十七項研究級機制**\ ；其對
  審查效率或採納率之效益本論文均\ **未予評估**\ ，於 §6.4.5 補上對應未來
  工作骨架 (s)。
- **研究級機制計數維持十七項**：與 docs 之 ``research-extensions.rst``
  「All seventeen research mechanisms」一致；§3.7.22 與 §3.7.20 同屬已實作
  之 operability／orientation 整合（前者含一項推論 step、後者為純轉換），
  均不計入十七項。
- 不變項目（沿用 v3.3）：仍\ **不謊造、不新增 RQ、不新增參考文獻**\ ；
  既有 §5 之表 1 / 表 2 / 表 3 不更動；§3.7.1–§3.7.21 之既有內容沿用。

本版相對於 v3.2 之關鍵差異（v3.3）：

- **新增 §3.7.20 可操作性與輸出整合**：對應隨附框架近期之 operability
  整合（SARIF / HTML 報告 / finding 抑制 / 去重 / 公開 API 影響 / Gitea
  平台 / commit message 審查 / Gemini・Cohere・Mistral 後端 / Router・
  Ensemble 組合 / self-consistency / step 外掛 / confidence 棄權 / 引用
  驗證 / injection 防護 / 在地化 / golden 快照 / benchmark 骨架 / 成本
  預算 / 聚焦審查模式 / Prometheus 告警規則）。皆為 runner-safe 純轉換
  或轉接器、隨附單元測試，\ **不計入 §3.7 之十七項研究級機制**\ ；其對
  審查品質之效益本論文均\ **未予評估**\ 。
- **新增 §3.7.21 僅設計、尚未實作之機制**：平行 per-file 審查、可配置
  step DAG、per-author 校準 / 自動調校 RAG 閾值 / embedding 漂移監測、
  server queue + rate-limiting 與 per-model 指標標籤。此類\ **不隨附
  程式碼**\ ，列為未來工作並標示\ **未予評估**\ 。
- **§1.5 第六項貢獻**\ 之後端清單補列 Gemini / Cohere / Mistral 與
  ``RouterBackend`` / ``EnsembleBackend`` 組合層。
- **研究級機制計數維持十七項**：與 docs 之 ``research-extensions.rst``
  「All seventeen research mechanisms」一致；新增之 §3.7.20 / §3.7.21
  分屬「operability 整合（已實作）」與「design-only（未實作）」兩類，
  均不計入十七項。
- 不變項目（沿用 v3.2）：仍\ **不謊造、不新增 RQ、不新增參考文獻**\ ；
  既有 §5 之表 1 / 表 2 / 表 3 不更動；§3.7.1–§3.7.19 之既有內容沿用。

本版相對於 v3.1 之關鍵差異（v3.2）：

- **§3.7.17 由單一 ``/kg/`` 路由精修為每倉 ``/kg/<name>/`` 路由**：
  v3.1 之知識圖譜視覺化僅服務單一 ``/kg/`` 靜態頁；隨附框架現以
  ``visualize-kg --name <name>`` 輸出 ``repo-kg-<name>.html``，並於
  nginx 以 ``^/kg/(?<repo>[A-Za-z0-9._-]+)/?$`` 正則路由，使單一主機
  得同時託管多倉之圖譜。此為 §3.7.17 之就地精修。
- **新增 §3.7.19 推論伺服器之指標端點與監控可觀測層**：將自架 FastAPI
  推論伺服器之 ``/metrics`` 端點（經 ``prometheus_fastapi_instrumentator``）
  與 ``docker-compose.monitoring.yml`` 之 Prometheus / Grafana /
  dcgm-exporter / cAdvisor 監控疊加層納入框架設計貢獻。此層與 §3.7.14
  同屬部署 / 可觀測層工程，\ **不計入 §3.7 之十七項研究級擴充機制**\ ；
  其端到端營運效益本論文均\ **未予評估**\ ，於 §6.4.5 補上對應未來工作
  骨架 (r)。對應 docs 之 ``research-extensions.rst`` 維持「seventeen
  mechanisms」，監控層之文件歸於 ``docker-platforms-report.rst``。
- **機制計數維持十七項**：§1.5 第七項貢獻、§1.3、§3.7 引言、§6.4.5 與
  self-audit 清單之研究級機制數沿用「十七項」，與 docs 對齊。
- 不變項目（沿用 v3.1）：仍\ **不謊造、不新增 RQ、不新增參考文獻**\ ；
  既有 §5 之表 1 / 表 2 / 表 3 不更動；§3.7.1–§3.7.18 之既有內容沿用
  （§3.7.17 除上述路由精修外不變）。

本版相對於 v3 之關鍵差異（v3.1）：

- **§3.7 機制清單由 13 項擴充為 17 項**：v3 定稿後，隨附開源框架另實作
  四項機制──主動學習衍生規則（`derive-lessons` + `--lessons`，§3.7.15）、
  跨 PR finding 聚類（`discover-rules`，§3.7.16）、Repo 知識圖譜
  （`build-kg` + `--kg-ground`，含 D3 視覺化，§3.7.17）、每檔遞增存檔
  與崩潰安全部分結果（`--incremental-save-dir`，§3.7.18）。各機制之
  端到端品質效益本論文均\ **未予評估**\ ，於 §6.4.5 各補上對應未來
  工作骨架 (n)–(q)。
- **§3.7.14 部署層補 (h)–(p)**：v3 定稿後另補上九項生產穩定性工程──
  step 輸出字元上限以避免 total_summary 階段 attention OOM (h)、本機後端
  之 FlashAttention 2 / SDPA 與 CUDA 13.0.1-devel 基底鏡像啟用 (i)、
  client 與 backend 之 timeout 預算由 30 分鐘拉長至 1 小時 (j)、poll
  重試預算由 5 提升至 60 並加上指數 backoff 以吸收 30B-class 後端重啟
  / GPU reload 所致之短暫 502 (k)、CI matrix 內以 ``actions/cache``
  串接 §3.7.5 之 diff-since-last SQLite 使單檔 fix 之 re-push 僅令該檔
  重跑 (l)、GitHub 留言 65,536 字元上限之保留 marker 之自動截斷以避免
  aggregate 階段 422 失敗 (m)、per-PR 狀態快取與 enumerate 階段之 matrix
  預過濾使未變動檔不再 spawn shard 而非僅於 runner 內短路 LLM (n)、每
  shard 寫 checkpoint 使 aggregate 失敗或 runner 崩潰時下次 push 仍能
  跳過已完成之檔 (o)、inline findings 對 diff hunks 之預過濾以避開 GitHub
  review API 因單筆虛構行號而 422 拒絕整份 review (p)。
- **§1.5 第七項貢獻**\ 之計數由「十三項」改為「十七項」並補列四項機制名稱；
  §1.3 TCSE 短文之對應字句同步更新計數。
- **§6.4.5 補 (n)–(q)**：四項新機制各補一段最小可驗證實驗骨架；現有
  (a)–(m) 段落沿用。
- 不變項目（沿用 v3）：仍\ **不謊造、不新增 RQ、不新增參考文獻**\ ；
  既有 §5 之表 1 / 表 2 / 表 3 不更動；§3.5 / §3.6 / §5.3 / §6.4.1–4
  沿用；§3.7.1–§3.7.14 之既有內容沿用。

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

> 本研究隨附之開源框架另實作十七項研究級擴充機制（涵蓋 prompt-injection
> robustness、closed-loop 多輪對話、counterfactual / mutation-style
> 審查、provenance 稽核、force-push 差分、suggestion sandbox 驗證、
> cross-language API drift、PR 類型自適應、reproducibility 訊號、
> dependency upgrade impact、reviewer personas + conflict surfacing、
> risk-weighted attention、diff entropy 偵測、以作者反饋語料主動學習
> 出之衍生規則（active-learning derived lessons）、跨 PR finding
> 聚類（self-discovered rules）、Repo 知識圖譜接地（symbol-grounded
> review）與每檔遞增存檔之崩潰安全部分結果（crash-safe partial
> review）），均以 CLI flag 之 opt-in 形式提供；其端到端品質效益本
> 研究均未予量化評估，詳細之設計說明與後續實驗骨架見學位論文 §3.7
> 與 §6.4.5（對應本框架之 GitHub 倉庫之
> `docs/en/concepts/research-extensions.rst`）。

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
>    端點、Anthropic Messages API 與 Gemini / Cohere / Mistral 等具體
>    後端，另以 ``RouterBackend``（失敗逐級回退）與 ``EnsembleBackend``
>    （多後端表決）提供組合層，並以 MCP server 將審查管線暴露為 IDE
>    可直接調用之 tool。本論文 §5 之實驗以本機後端為主，跨後端比較與
>    IDE 內審查觸發率之評估屬未來工作。
> 7. **十七項研究級擴充機制之設計**（見 §3.7 詳述）：包含 prompt-injection
>    robustness 之 corpus + bypass detection、closed-loop 多輪對話、
>    counterfactual / mutation-style 審查、provenance 稽核、force-push
>    差分 cache、suggestion sandbox 驗證、cross-language API drift
>    偵測、PR 類型自適應、reproducibility 訊號、dependency upgrade
>    impact 分析、reviewer personas + conflict surfacing、risk-weighted
>    attention、diff entropy / 「diff bomb」偵測、作者反饋語料主動
>    學習出之衍生規則、跨 PR finding 聚類自我發現規則、Repo 知識
>    圖譜對 inline finding 之符號接地，與每檔遞增存檔之崩潰安全部分
>    審查結果。每項對應一個 CLI flag、一份單元測試與
>    `docs/en/concepts/research-extensions.rst` 內之設計說明；其端到
>    端品質效益本論文均未予評估，列為 §6.4.5 所述之未來工作。

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
> 本節描述本研究隨附之開源框架另實作之十七項機制，均對應於 LLM 程式
> 碼審查文獻中目前較少實作之研究面向。每項機制皆以 CLI flag 形式
> opt-in，預設關閉以維持 §5 所驗證之 baseline pipeline 不受干擾。
> 本論文\ **未對任何單項機制之端到端品質效益進行量化評估**\ ；
> §6.4.5 將就每項機制給出對應之未來工作骨架。所列機制皆已伴隨單元
> 測試與設計文件（`docs/en/concepts/research-extensions.rst`），可
> 直接於工程上使用，僅缺學術評估。子節編號 §3.7.1–§3.7.13 為 v3 既有
> 之十三項；§3.7.14 為部署層之工程設計；§3.7.15–§3.7.18 為 v3.1 新增
> 之四項機制；§3.7.19 為 v3.2 新增之可觀測層工程，與 §3.7.14 同屬部署
> 層、不計入上述十七項研究級機制；§3.7.20 為 v3.3 新增之可操作性與輸出
> 整合（已實作並附單元測試，亦不計入十七項），§3.7.21 為僅設計、尚未
> 實作之機制骨架。
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
> (h) **Step 輸出字元上限以避免 final-step OOM**：CoT 最終
> ``total_summary`` 步驟之 prompt 為前序所有步驟之輸出之串接；於預設
> `max_new_tokens=32768` 下，前序四步各可吐 ~120 KB，使最終 prompt
> 易達數十萬 token 並於 attention 計算階段觸發 GPU OOM（50K token
> × 64 head 之 KV cache 約需 300 GiB）。框架以
> `_DEFAULT_MAX_STEP_RESULT_CHARS = 6000`（約 1500 token）對\
> ``ctx.results`` 內每步之 in-pipeline 副本做硬上限截斷，輸出至磁碟
> 與 API response 之全文保留不動；該上限可由
> ``PRTHINKER_MAX_STEP_RESULT_CHARS`` 環境變數於 server 端覆寫。
>
> (i) **本機後端之 FlashAttention 2 / SDPA 啟用與容器基底升級**：將
> ``transformers.AutoModelForCausalLM.from_pretrained`` 之
> ``attn_implementation`` 偏好設為 ``flash_attention_2`` 並 fallback 至
> ``sdpa``，使 30B-class MoE 之 attention 計算避開 vanilla 路徑之
> O(L²) 記憶體峰值；配合升級伺服器 Dockerfile 之 CUDA 基底至 ``13.0.1
> -devel-ubuntu22.04`` 以於映像建構期間提供 flash-attn 之 nvcc，並將
> ``peft`` 釘住至 ``0.18.0`` 與 LoRA adapter 訓練時版本對齊（``peft``
> ``0.19.x`` 將 MoE 之 expert projection（``gate_proj`` / ``up_proj`` /
> ``down_proj``）改派至 ``ParamWrapper``，拒絕訓練時之
> ``lora_dropout=0.1``）。
>
> (j) **timeout 預算之兩端拉長**：原 v3 設計之 client poll deadline
> 與 backend per-call timeout 均為 30 分鐘；於本機後端跑全 5 步 CoT
> 之 per-file review 觀察到 30B 模型於 ``total_summary`` 步驟之單一
> generate 呼叫可逼近此上限。框架將 ``RemoteBackendConfig.
> timeout_seconds`` 之預設值由 1800.0 提升至 3600.0、CLI 客戶端之
> deadline 同步至 1800.0 / 3600.0，並於 ``review`` 子指令文件明示
> 該上限為「全 pipeline 之 wall-clock 上限，非單一 HTTP round-trip
> 之 idle timeout（後者由 reverse-proxy 控管）」。
>
> (k) **poll 重試預算與指數 backoff 以吸收短暫 502**：30B-class
> 後端之 process 重啟、GPU reload、nginx config reload 易於 ~1 分鐘
> 時段內持續吐 502；原 v3 之
> ``_MAX_CONSECUTIVE_POLL_FAILURES = 5`` × ``_POLL_INTERVAL_SECONDS
> = 5`` 僅能扛 ~25 秒，超過即丟 ``HTTPStatusError`` 並中斷整輪
> review。框架將預算提升至 60 並引入 ``_POLL_BACKOFF_AFTER_FAILURES
> = 5`` / ``_POLL_MAX_INTERVAL_SECONDS = 30.0``：前 5 次失敗仍以
> 5 秒等距重試，第 6 次起以 2 倍 backoff 增長至 30 秒上限，總可
> 容忍時段約 3 分鐘；超出仍 raise，並由 ``_send_cancel`` 主動於
> ``finally`` 區塊送 ``/review/cancel`` 釋放 GPU。
>
> (l) **CI matrix 內之 diff-since-last 快取串接**：§3.7.5 所述之
> force-push 差分機制原僅於 CLI 使用層暴露
> ``--diff-since-last`` flag 與 SQLite cache 檔；於 CI 環境下需搭配
> GitHub Actions 之 ``actions/cache`` 機制方能跨 workflow run 保留。
> 框架於 matrix shard 之 review 步驟前後分別加入
> ``actions/cache/restore`` 與 ``actions/cache/save``，以
> ``prthinker-diff-pr-<PR>-<run>-<shard>`` 為精確 key 並以
> ``prthinker-diff-pr-<PR>-`` 為 prefix restore-key 抓取同 PR 上最
> 近一次成功 run 之 cache；同時於 env 注入
> ``PRTHINKER_DIFF_SINCE_LAST=true`` 使 ``review-pr`` 對每檔之 post-
> change 內容做 hash。``save`` 步驟以 ``if: always()`` 包裹，即使
> shard 中途失敗，已 hash 之檔仍寫回 cache 供下一次 push 跳過。本
> 機制使單檔小幅 fix 之 re-push 僅令該檔重跑 CoT，其餘 N-1 個 shard
> 命中 cache 即直接 reuse 前次 findings。本子項屬部署層工程貢獻；
> 其於真實 PR 流量上之 GPU-second 節省與 cache hit 比率本論文未予
> 評估。
>
> (m) **GitHub 留言之 65536-char 上限自動截斷**：GitHub Issues /
> PR 之 comment body 超過 65,536 字元時回應 422 Unprocessable
> Entity；於多檔 matrix run 之 aggregate 階段，將各 shard 之 per-
> file 區塊（含 §3.7.14 (g) 之 Overall Summary、RAG docs、judge
> verdicts）串接於同一 upserted 留言中，極易超過該上限而導致整輪
> aggregate 失敗。框架於 ``upsert_pr_comment`` 內加上 60,000 字元
> 之硬上限 ``_GITHUB_COMMENT_BODY_MAX``：超過時保留前 60,000 字之
> 主體並追加 truncation 通知（指向 matrix shard 之 job log 取完整
> per-step 內容），並\ **保證\ ``comment_marker`` 字串於截斷後仍位
> 於開頭**\ ，使下一次之 upsert 仍能定位同一留言並 PATCH 之，而非
> 重新 POST 一條新的（避免破壞 §3.7.14 (f) 之 idempotency 設計）。
> 本子項屬部署層工程貢獻；其於真實長 PR 上之截斷率與 reviewer 點
> 入 job log 之頻率本論文未予評估。
>
> (n) **enumerate 階段之 per-PR 狀態快取與 matrix 預過濾**：
> §3.7.14 (l) 之 in-runner SQLite cache 只能讓 shard 內之 LLM
> 短路，無法避免每個未變動之檔仍消耗一個 runner 之 checkout +
> ``setup-python`` + ``pip install`` + healthcheck（~1–2 分鐘）。
> 框架另引入「per-PR 狀態快取」\ 之 enumerate 預過濾：每 PR 之
> ``actions/cache`` 條目包含
> ``.prthinker/pr-state/manifest.json``（路徑 → blob SHA 對照表，
> blob SHA 由 ``git rev-parse HEAD:<path>`` 取得，與 GitHub API
> 之回應一致）與 ``.prthinker/pr-state/partials/<sha256>.json``
> （該檔上次 review 之 partial result）。enumerate job 先 restore
> 該快取，逐 PR file 比對其當前 blob SHA 與 manifest，命中者直接
> 自 matrix 中剔除\ **不再 spawn shard**\ ，已 reuse 之 partial
> 上傳為 ``partial-skipped`` artifact 供 aggregate 與新跑之 shard
> 之 partial 一同 merge；aggregate post 完成後，``write-state``
> 步驟以 PR head 重建 manifest 與 partials 並做 canonical
> ``cache/save@v4``，作為下一次 push 之來源。並同時修復 v3 設計
> 中之 env-var 名稱錯位（``REVIEWMIND_DIFF_SINCE_LAST`` /
> ``.reviewmind/diff-cache.sqlite`` 重新命名為對應之
> ``PRTHINKER_*``），使 (l) 之 in-runner SQLite 短路成為第二層
> 安全網。本子項屬部署層工程貢獻；其相對 (l) 之邊際 CI 分鐘節省
> 本論文未予評估。
>
> (o) **每 shard 之狀態 checkpoint 寫入**：(n) 設計中之 canonical
> state 由 aggregate job 寫入；若 aggregate 失敗或 runner 於最後
> 一個 shard 與 aggregate 之間崩潰，整輪所跑之 review 均不被下次
> push 利用。配合 §3.7.14 (b) 之 ``max-parallel: 1``（既為單 GPU
> 之必然設計，亦提供本子項所需之序列性），框架讓每 shard 於
> ``review-pr`` 成功後執行三步：(i) 將其 ``partial.json`` 複製至
> ``.prthinker/pr-state/partials/<sha256(path)>.json``；(ii) 將
> ``{path, blob_sha}`` 追加至 ``manifest.json``；(iii) 以
> ``-shard-<index>`` 後綴另寫一筆 cache entry。aggregate 若成功
> 寫入無後綴之 canonical entry 則自動取代所有 shard checkpoint；
> aggregate 失敗時，下次 push 之 restore-keys prefix 仍可抓到最
> 後一個成功 shard 之 checkpoint，使所有「於 aggregate 失敗\ **前**\
> 已完成 review 之檔」於下次 matrix 中跳過。``[ -s partial.json ]``
> 守門確保 backend 不通之 shard（review step 雖以 exit 0 結束但
> 未產出 partial）不會把空結果寫進 manifest 而於下次被當作
> 有效 reuse。本子項屬部署層工程貢獻；其於人為注入之 aggregate
> 失敗實驗下之 CI 分鐘節省量本論文未予評估。
>
> (p) **inline findings 對 diff hunks 之預過濾以避開 review 全
> 局 422**：GitHub 之 PR Review API 對單一 inline comment 若指
> 向 ``side:RIGHT`` 之非 hunk 範圍行，將以 422 Line could not
> be resolved 拒絕\ **整份 review**──一條虛構行號之 finding 即
> 連帶癱瘓同 review 內所有合法 finding，aggregate 因此 short-
> circuit 而 ``close_gate`` 不執行，required-status branch
> protection 將永遠看不到綠燈而阻擋 merge。框架施兩道防線：(i)
> ``github_api._filter_findings_to_diff`` 解析 PR diff 之 hunk
> header（``@@ -a,b +c,d @@``\ ），對 ``' '`` / ``'+'`` 兩種
> 行種逐行追蹤 new-side 行號集合，丟棄
> ``(path, line) ∉`` 該集合之 finding 與
> ``start_line`` 越 hunk 之 multi-line finding；diff 抓取失敗
> 之 fall-through 路徑改由外層 try/except 接住而非中斷。(ii)
> ``_cmd_aggregate`` 將 ``submit_inline_review`` 包入 try/except
> ──summary comment 與 check run 於該時點均已開立，犧牲 inline
> 標注屬可接受損失，但若 check run 之 ``close_gate`` 因連動異常
> 而未執行則 PR 永遠卡住。本子項屬部署層工程貢獻；其於真實 PR
> 上每輪 review 之被預過濾 finding 數中位數本論文未予評估。
>
> 本機制屬部署層設計貢獻，其對端到端 PR 流量之穩定性、wall-clock
> 改善、reviewer 對重複留言之認知負擔等量化評估本論文未予進行，
> 列為 §6.4.5 之未來工作。
>
> 3.7.15  主動學習衍生規則（active-learning derived lessons）
>
> §3.5 所述之 dismissed / accepted 兩語料為一階訊號──「此筆具體
> 留言被作者拒絕」「此筆具體建議被採納」──兩者本身對未來 PR 無泛化
> 能力。框架於兩語料之上再加一層：``derive-lessons`` 子指令讀取兩
> 語料之最近 N 筆，向模型詢問「應從中抽出何種可重用之審查規則
> （``name`` / ``trigger`` / ``action`` 三欄）」，並明示模型「輸出
> 空陣列優於虛構規則」。解析後之 ``LessonRule`` 連同其來源 PR 編號
> 一併追加寫入 ``lessons.jsonl``（append-only，供事後可追溯地檢視
> 規則演化）。下一次 ``review-pr --lessons`` 時，最近 K 條規則被渲
> 染為「Repo-derived review lessons」區塊，前置注入 inline-findings
> prompt，模型被指示將其視為軟性指引而非硬規則。本機制屬框架設計
> 貢獻；其對作者反饋語料累積後之 inline finding 精確率影響本論文
> 未予評估。
>
> 3.7.16  跨 PR finding 聚類與自我發現規則
>
> 若框架反覆於不同 PR 中提出實質相同之 finding，正確之回應不是繼續
> 重複，而是將其結晶為 ``--rules-dir`` 下之 repo 規則。框架為每條
> 已產出之 inline finding 將留言文字以 backend embedding 化並與
> ``(pr_number, file_path, line, comment, embedding)`` fingerprint
> 一併寫入 ``findings-index.sqlite``。``discover-rules`` 子指令對
> 該 store 跑貪婪餘弦相似度聚類（預設 brute-force NumPy；大規模時
> 可換為 ``sqlite-vec`` / FAISS 而不更動 ``greedy_cluster`` API），
> 列出超過 ``--min-cluster-size`` 且 ``--similarity-threshold`` 以上
> 之 cluster 並以其\ **最新一筆**\ 為代表（使候選規則隨時間追隨團隊
> 用語演化而非僵化於舊用詞）。框架\ **不**\ 自動寫入規則檔──候選
> 必須由人類審查者明示採納。本機制屬框架設計貢獻；其聚類純度與所
> 衍生規則之實際採納率本論文未予評估。
>
> 3.7.17  Repo 知識圖譜與 inline finding 之符號接地
>
> LLM 審查器於大型 repo 上常見之失敗模式為虛構符號名稱──宣稱
> ``auth.py`` 內有 ``get_user`` 函式而該函式實際位於 ``core/users.py``。
> 既有 RAG 層接地於 repo 之\ *規則*\ ，本機制接地於 repo 之\ *符號*\ ：
> ``build-kg --workdir .`` 以 Python ``ast`` 走訪
> ``def`` / ``class`` / 類方法 / ``ALL_CAPS`` 常數，並以正則為主之
> scanner 走訪 TypeScript / JavaScript 之
> ``function`` / ``class`` / ``interface`` / ``const`` / ``default``
> export，將 ``(symbol, kind, file, line, parent)`` 持久化於
> ``.prthinker/repo-kg.sqlite``。store 以 ``workdir`` 為 key，單一
> SQLite 檔可同時容納多 repo 之 KG 而無洩漏。``review-pr --kg-ground``
> 將該表渲染為「Known symbols (treat as canonical, do not
> hallucinate)」前置區塊，並明示「finding 內若引用符號，該符號必須
> 出現於表中」。``rebuild()`` 採整批替換（先 delete 該 workdir 之
> 舊 rows 再插入），確保 store 與 HEAD 對齊；增量更新列為未來工作。
> 框架另提供 ``visualize-kg`` 子指令將該 SQLite 表輸出為單頁 D3
> HTML 互動視圖；``visualize-kg --name <name>`` 將其寫為
> ``repo-kg-<name>.html``，並於監控疊加層之 nginx 以
> ``^/kg/(?<repo>[A-Za-z0-9._-]+)/?$`` 正則路由 ``/kg/<name>/``，預設
> ``/kg/`` 則服務單倉之 ``repo-kg.html``；``<name>`` 之合法字元集與
> nginx 路由一致，故不可路徑穿越。單一主機由此得同時託管多倉之圖譜，
> 使團隊可線上瀏覽框架對各 repo 之符號理解。本機制屬框架設計貢獻；其
> grounded prompt 對符號虛構率之降幅與對 inline finding 精確率之影響
> 本論文未予評估。
>
> 3.7.18  每檔遞增存檔與崩潰安全部分結果（crash-safe partial review）
>
> 30B-class 後端之 per-file CoT 於大 PR 上可累積跑數十分鐘。當該輪
> 因 idle-poll sweep（§3.7.14 (e)）、GPU OOM、runner timeout 或人工
> 於 GitHub Actions 介面之 cancel 而中途終結時，原 v3 之
> ``--output-json`` 僅於審查最末整批落盤──中途死亡即\ **無**\ 任何
> 部分結果可審視。框架以 ``--incremental-save-dir <path>`` 將
> per-file 完成事件改寫為「即時 atomic 寫盤」：
>
> - ``<path>/files/<slug>.json``：``FileReviewResult`` 加入記憶體
>   ``per_file_results`` list 之同時，將其序列化（涵蓋
>   ``inline_findings`` / ``verdict`` / ``counterfactuals`` 等所有
>   pydantic 欄位）寫入磁碟；slug 將目錄分隔符與非法字元一律換為
>   ``_`` 以跨 Windows / Linux / macOS 通用。
> - ``<path>/review.json``：\ **僅於**\ 整輪 sweep 跑完寫入；其存在
>   即意味著「該次 run 乾淨完成」。
> - ``<path>/meta.json``：開始時寫入 ``repo`` / ``pr_number`` /
>   ``head_sha`` / ``started_at``，使事後檢視者可辨識所屬 PR / commit。
>
> 所有寫盤透過 ``<target>.tmp`` + ``os.replace`` 達成原子性，半寫
> 狀態不可見。Writer 內部之任何 ``OSError`` 僅 log 並吞掉──持久化
> 之失敗不可中斷正在跑之 review。``CoTPipeline.run_per_file`` 為此
> 暴露 ``on_file_done`` callback，於 cache-hit 與全 review 兩處
> append 點各觸發一次；本機制限於本機 pipeline 路徑（遠端 pipeline
> 走 ``--use-remote-pipeline`` 時 server 一次回完整 ``ReviewResult``，
> per-file 增量在伺服端不適用，``--output-json`` 仍為其對應之單檔
> 落盤路徑）。本機制屬框架設計貢獻；其於真實 CI 流量上之「中斷
> -recovery 收益」量化評估本論文未予進行。
>
> 3.7.19  推論伺服器之指標端點與監控可觀測層（observability）
>
> 自架之 FastAPI 推論伺服器以 ``prometheus_fastapi_instrumentator``
> （Prometheus 之 FastAPI 中介層）將每端點之請求數、延遲與狀態碼以
> Prometheus 文字格式暴露於 ``/metrics``。本機制與 §3.7.14 同屬部署 /
> 可觀測層工程，不計入本節之十七項研究級擴充機制。該相依採延遲匯入（lazy
> import），未安裝時僅記錄一行 log 並停用該端點，故 runner-profile
> 安裝（``httpx + pydantic + PyYAML``）不受影響。隨附之
> ``docker-compose.monitoring.yml`` 監控疊加層另編排 Prometheus（抓取
> ``/metrics``）、Grafana（儀表板）、dcgm-exporter（GPU 指標）與
> cAdvisor（容器指標）四個服務，並由 nginx 以 ``/grafana/`` /
> ``/prometheus/`` / ``/cadvisor/`` / ``/kg/`` 之路徑反向代理。本機制
> 屬框架之可觀測性與部署工程設計貢獻；其對營運者故障定位時間之助益
> 與指標蒐集之執行期額外開銷本論文未予評估。
>
> 3.7.20  可操作性與輸出整合（operability and output integrations）
>
> 除上述十七項研究級機制外，隨附框架另提供一組 opt-in 旗標／子指令，
> 將審查結果與外部工具鏈整合。此類功能皆為純轉換或轉接器（不含推論），
> 故於 runner profile（``httpx + pydantic + PyYAML``）即可執行，且皆
> 隨附單元測試；其對審查品質或實務採納率之效益不在本論文評估範圍：
>
> - **SARIF 匯出**（``--sarif-out``）：以 SARIF（Static Analysis Results
>   Interchange Format，靜態分析結果交換格式）2.1.0 輸出 finding，供
>   GitHub code-scanning 或任何 SARIF 檢視器使用。
> - **HTML 報告**（``--html-report``）：產生獨立、防 XSS（cross-site
>   scripting，跨站腳本）之 HTML 審查報告（嚴重度摘要 + 每檔 finding）。
> - **finding 抑制**（``--ignore-file`` / ``.prthinkerignore``）：以路徑
>   glob、``severity:<level>`` 或 ``rule:<id>`` 丟棄 finding；缺檔即 no-op。
> - **finding 去重**（``--dedupe-findings``）：合併近似重複之 finding
>   （同 path+line、等義訊息，保留最高嚴重度）。
> - **公開 API 影響**（``--api-impact``）：以對 diff 內公開 ``def`` /
>   ``class`` 簽章增刪改之啟發式掃描，於摘要附 semver（Semantic
>   Versioning，語意化版本）影響（major / minor / patch）一行。
> - **Gitea 平台**（``--platform gitea``）：與 GitHub / GitLab 同走
>   ``PlatformAdapter`` 策略之 ``GiteaAdapter``。
> - **commit message 審查**（``review-commits``）：就 stdin 讀入之 commit
>   message 評估其品質（conventional-commits、祈使語氣、清晰度）。
> - **額外推論後端**（``--backend gemini|cohere|mistral``）：與 OpenAI /
>   Anthropic 同走 ``InferenceBackend`` 工廠之 HTTP 後端。
> - **後端組合**（library API）：``RouterBackend`` 於失敗時逐級回退、
>   ``EnsembleBackend`` 查詢多後端並依 ``longest`` / ``first`` /
>   ``majority`` 選取；二者皆為 ``InferenceBackend`` 裝飾器，可與快取／
>   telemetry 包裝層組合。
> - **self-consistency 取樣**（library：``self_consistent_generate``）：
>   對同一 prompt 取樣 k 次後回傳多數（正規化）輸出。
> - **第三方 step 外掛**（``load_plugin_steps``）：以 ``prthinker.steps``
>   entry-point group 探索外部套件所註冊之審查 step，於 CLI 啟動時載入，
>   使外部套件無需改動核心即可註冊 step（Open/Closed 原則）。
> - **confidence 棄權**（``--min-confidence``）：丟棄 ``provenance``
>   confidence 低於閾值之 finding（須搭配 ``--provenance``）；無
>   confidence 者一律保留。
> - **引用驗證**（library：``citation_verify``）：標記 provenance 引用之
>   rule / example 索引越界、或 diff 證據行落在 diff 之外者。
> - **prompt-injection 防護**（library：``injection_guard``）：對新增行
>   啟發式掃描（直接注入、role-hijack、編碼 blob），補強對抗語料。
> - **finding 在地化**（library：``localize``）：以 prompt + parse 將
>   finding 留言翻譯為目標語言。
> - **golden-set 快照**（library：``golden``）：寫入／比對 finding 之
>   穩定快照以偵測 prompt／行為漂移（不含任何分數）。
> - **評估 harness 骨架**（library：``benchmark``）：將 case 語料跑過
>   後端並僅記錄原始輸出；依 ``paper_rule.md`` 不輸出任何分數或聚合數字。
> - **成本估算與預算**（library：``cost``）：自 ``pricing`` 估每次呼叫
>   之 USD，並以 ``CostBudget`` 為單一 PR 設定上限。
> - **聚焦審查模式**（``--review-modes security,performance,…``）：以
>   Registry 模式註冊於 ``prthinker.review_modes`` 之 opt-in 全 diff
>   pass──security / SAST（Static Application Security Testing，靜態
>   應用程式安全測試）、performance、test-coverage、IaC（Infrastructure
>   as Code，基礎設施即程式碼）、DB-migration、accessibility、
>   secret-scan、PII（personally identifiable information，個人可識別
>   資訊）；未知名稱略過。
> - **Prometheus 告警規則**（``docker/monitoring/alerts.yml``）：監控疊
>   加層隨附之告警規則（詳見 Docker 概念頁與 §3.7.19）。
>
> 上列整合屬部署 / 輸出層工程，\ **不計入 §3.7 之十七項研究級擴充
> 機制**\ ；各功能皆以單元測試覆蓋，惟其對審查品質或實務採納率之
> 量化效益本論文未予評估。
>
> 3.7.21  僅設計、尚未實作之機制（design-only, not yet implemented）
>
> 下列機制於隨附框架中\ **僅以設計描述存在、未隨附程式碼**\ ，因其素樸
> 實作將不安全或需大幅重寫；依 ``paper_rule.md`` 皆標示「本論文未予
> 評估」並列為未來工作：
>
> - **平行 per-file 審查**：併行審查各檔可縮短 wall-clock，惟行內 GPU
>   後端（``LocalHFBackend``）序列化生成、不可由多執行緒安全呼叫；正確
>   設計需 per-backend 併發能力旗標加上有界 worker pool（僅 HTTP 後端
>   opt-in、本機後端不參與）。
> - **可配置 step DAG（directed acyclic graph，有向無環圖）**：管線目前
>   為固定線性 step 序列；分支／條件式 DAG（依 PR 類型跳過 step、獨立
>   step 扇出）需重構 ``CoTPipeline`` 與 step 解析。
> - **per-author 校準 / 自動調校 RAG 閾值 / embedding 漂移監測**：均需
>   累積 accept / dismiss 歷史與線上回饋迴路；語料庫已存在，惟學習迴路
>   僅止於設計。
> - **server queue + rate-limiting 與 per-model 指標標籤**：伺服端併發
>   控制與更細之 telemetry 標籤；為維持 boot path 與指標基數穩定，目前
>   僅止於設計。
>
> 本子節所列皆\ **不隨附程式碼**\ ，與 §3.7.1–§3.7.20 之「已實作」性質
> 不同，純屬未來工作之設計骨架。
>
> 3.7.22  審查導覽與分流輔助（review orientation and triage aids）
>
> 多數審查器僅輸出 finding，卻未協助審查者\ **規劃如何閱讀**\ 一份變更。
> 隨附框架另提供一組 opt-in 之導覽／分流輔助。其中唯一使用推論者為
> **逐檔變更走查**（``--walkthrough``）：於 per-file 管線新增一個
> ``WalkthroughStep``，就每檔 diff 產出二至四句「此變更做了什麼、為何」
> 之敘事（僅描述、不評斷，亦不得臆造 diff 未顯示之行為），釘於該檔區塊
> 最上方。此為既有\ **無推論**\ 之 commit-message PR 概覽之推論側對應物，
> 使審查者於閱讀 finding 前先掌握「變更之意圖」。其餘輔助皆為 runner-safe
> 純轉換、於 runner profile 即可執行：
>
> - **Conventional Comments 標籤**：依嚴重度與 category 為每則 inline 留言
>   冠以 ``issue`` / ``suggestion`` / ``nitpick`` 標籤（共用 formatter，
>   GitHub 與 Gitea 一致），使阻擋性與可選項可被人與工具一眼分流。
> - **跨檔 Top-findings 佇列**：將全部 finding 依嚴重度再依模型 confidence
>   排序之單一優先清單，較僅含 error 之 Must-fix 為廣。
> - **Must-fix 原始碼行引用**：自 diff 解析出問題行內容，使阻擋性問題不必
>   開檔即可閱讀。
> - **每檔變更規模徽章**（``+a −b · h hunks``）、**建議審閱順序**
>   （``--review-order``，以 KG import 入度將最被依賴之檔排前）、**變更地圖**
>   （``--change-map``，以 Mermaid 畫變更檔間之 import 邊）、**缺測試提示**
>   （改了 production ``.py`` 卻無同名測試變更之啟發式）、**high-risk 檔案
>   註記**（``--risk-weighted`` 已算之 churn／複雜度／bug 歷史分數）與
>   **reviewer checklist**（自未驗證 error、低再現性 finding、API drift 生成
>   之人工把關清單）。
>
> 上列導覽／分流輔助屬輸出 / 呈現層，\ **不計入 §3.7 之十七項研究級擴充
> 機制**\ ；各功能皆以單元測試覆蓋，惟其對審查效率、缺陷遺漏率或實務採納
> 率之量化效益本論文未予評估；對應未來工作骨架見 §6.4.5 (s)。

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
> 6.4.5  §3.7 所述十七項研究級擴充機制之實證評估
>
> §3.7 所述十七項機制目前僅完成框架實作；其端到端品質效益需後續以
> 真實 PR 流量驗證。為避免日後補實驗時設計分歧，本節為各機制標示最
> 小可驗證實驗骨架；所列指標皆為公開可重現之量度，避免引入新主觀
> 量表。v3 既有之 (a)–(m) 對應 §3.7.1–§3.7.13；v3.1 新增之 (n)–(q)
> 對應 §3.7.15–§3.7.18；(r) 對應 §3.7.19 之可觀測層（屬部署工程，不計
> 入十七項，列此便於對照）。
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
> (n) Active-learning derived lessons（§3.7.15）：先令 dismissed /
> accepted 累積至雙語料各 ≥ 100 筆後，於同一份固定 PR 集合上以
> paired bootstrap 比較啟用 ``--lessons`` 與否之 inline finding
> precision 與作者再次按 👎 比率。輔以時間切片：每週重跑
> ``derive-lessons``，比較其輸出之新規則與既有規則之 Jaccard 重疊，
> 量化規則庫之收斂速度。
>
> (o) Cross-PR finding clustering（§3.7.16）：於 ≥ 500 筆累積 finding
> 上以 ``discover-rules`` 跑全 grid 之 ``--similarity-threshold`` ∈
> {0.75, 0.80, 0.85, 0.90} × ``--min-cluster-size`` ∈ {3, 5, 10}；
> 以 ≥ 3 名人工審查者就「此 cluster 是否確為一條值得寫入規則庫之
> 真實重複規則」之 Likert 5 點評分作為品質指標，並計算評審間
> Cohen's κ。並以「成為框架候選 → 被人類採納為 rules-dir 條目」之
> 漏斗比率作為實用性指標。
>
> (p) Repo knowledge graph grounding（§3.7.17）：以 ≥ 30 個跨語言
> 大 repo 為樣本，於每 repo 上各跑啟用與未啟用 ``--kg-ground`` 之
> 全 PR 集合。以人工標記之「該 finding 提及之符號是否實際存在於
> repo」作為 ground-truth，計算「符號虛構率」之相對降幅；輔以
> ``--kg-ground`` 之 prompt token 開銷與每 PR wall-clock 之 trade-
> off 表。視覺化模組之效益另以團隊內部使用次數 / page-view 等
> 工程量度報告，不混入研究主張。
>
> (q) Crash-safe partial review（§3.7.18）：刻意於 CI 矩陣
> 中注入 N 次中斷（``concurrency: cancel-in-progress`` 觸發、
> 人工 cancel、模擬 GPU OOM 之 ``ask/cancel`` 連發），以
> ``--incremental-save-dir`` 啟用前後各跑 ≥ 50 次中斷實驗，比較
> 「中斷後可恢復之 per-file 完成數量」之中位數與「未恢復則需重跑
> 之 GPU-second 總開銷」之減幅。本項屬可靠性工程量化評估，與品質
> 研究分流。
>
> (r) 推論伺服器指標端點與監控疊加層（§3.7.19）：以固定之合成負載
> （固定 PR 集合連續送審）量測啟用 ``/metrics`` instrumentation 前後
> 之每請求延遲差與伺服器吞吐差，作為觀測開銷之上界；並以 ≥ 50 次注入
> 之故障情境（GPU OOM、後端重啟、502）量測「自告警觸發至營運者定位
> 根因」之時間，比較有無 Grafana 儀表板兩組之 MTTR（平均修復時間，
> mean time to repair）。本項屬可觀測性
> 工程量化評估，與品質研究分流。
>
> (s) 審查導覽與分流輔助（§3.7.22）：就\ **逐檔變更走查**\ ，以 ≥ 50 個
> PR 令 ≥ 3 名審查者就「走查是否縮短理解該檔變更之時間、是否準確反映
> diff 而無臆造」之 Likert 5 點評分與事實性誤判率作為效益與安全指標；
> 另以開啟與未開啟導覽輔助兩組量測「首條留言前之導覽時間」與缺陷遺漏率
> 之差。本項屬輸出 / 呈現層量化評估，與核心品質研究分流，不計入十七項。
>
> 上列十七組研究級實驗與 (r) 之可觀測層工程實驗、(s) 之導覽層實驗皆需累積實際語料；
> 本論文之主要貢獻仍為 §5.1 / §5.2
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
- [ ] 新增之子章節（§3.5.1–4、§3.6.1–2、**§3.7.1–21**、§5.3.1–3、
      §6.4.1–5）在 docx 內已以加粗 + 略大字級之段落呈現，不僅以段落
      換行示意。子節編號：§3.7.1–§3.7.13 為原 13 項機制、§3.7.14 為
      部署層含 (a)–(p)、§3.7.15–§3.7.18 為 v3.1 新增之四項機制、§3.7.19
      為 v3.2 新增之可觀測層工程（部署層，不計入十七項研究級機制）、
      §3.7.20 為 v3.3 新增之可操作性與輸出整合（已實作 + 測試）、§3.7.21
      為僅設計未實作之機制骨架；後三者皆不計入十七項。
- [ ] §1.5 條列之七項貢獻：前三項已對應 §5 表 1 / 表 2 / 表 3 之實驗
      結果；第 4–7 項已明示為「框架設計貢獻、量化驗證屬未來工作」。
      第 7 項已更新為「十七項」並包含 lessons / clusters / KG /
      incremental save 四項名稱。
- [ ] §3.5 / §3.6 / **§3.7** 全部段落內含「本論文未予評估」或等義之
      免責標示；§3.7 內提及「框架設計貢獻」之頻次 ≥ 17 次（每子節
      至少一次）。
- [ ] **§3.7 之十七項機制每項皆對應 §6.4.5 之一個未來工作骨架
      (a)–(m) ∪ (n)–(q)**，不漏項（(r) 為 §3.7.19 可觀測層之額外骨架，
      屬部署工程，不計入十七項）；§6.4.5 內每項皆給出具體之
      ground-truth 來源、語料規模下限、與不依賴人類主觀量表之量化
      指標。
- [ ] §5.3 之三段分析所引之每個數字皆可於表 1 / 表 2 / 表 3 中找到。
- [ ] §6.4 之五項未來工作皆對應到 §1.5 中已明示為「框架設計貢獻」之
      項目（6.4.1 ↔ 第 6 項後端 / 6.4.2 ↔ 第 5 項語料 / 6.4.3 ↔ 第 6
      項平台與多模型 / 6.4.4 ↔ 第 6 項 MCP / 6.4.5 ↔ 第 7 項十七項
      機制）。
- [ ] 文中所有「該方法」「上述」「此」之代名詞，往前 3 行內可找到具
      體指稱。
- [ ] 全文未出現「賦能 / 打造 / 全方位 / 深入探討 / 值得注意的是 /
      綜上所述（於結論章內）」等 AI 口頭禪。
- [ ] **十七項擴充機制之名稱於論文與隨附之 `docs/en/concepts/
      research-extensions.rst` 完全一致**（避免 `--reply-to-author`
      於論文內被翻為「多輪對話」、於 docs 內被翻為「閉環對話」之
      不一致；新增之 `--lessons` / `discover-rules` / `--kg-ground` /
      `--incremental-save-dir` 之中譯需與 research-extensions.rst 對齊；
      另 §3.7.19 之 `/metrics` 指標端點與監控疊加層之中譯需與
      docker-platforms-report.rst 對齊）。
- [ ] 已驗證每個 `<w:rPr>` 之 `<w:rFonts>` 元素四個 slot 皆設為標楷體 /
      Times New Roman。
- [ ] TCSE v2.3 之插入後總字元數仍可控制於 6 頁 Word 上限內；§3.7
      與 §6.4.5 主要針對學位論文 v1.8，TCSE 短文版本可僅於 §1.3 之
      末句後追加一句「本研究隨附之開源框架另實作十七項研究級擴充機
      制，詳見學位論文 §3.7 與 §6.4.5；該等機制之量化評估均屬未來
      工作」以同步而不超頁。

> 若任一項回答為「否」，於 commit 進 docx 之前先處理；尤其第一項
> （不謊造）為硬規則，違反即構成研究不當行為。
