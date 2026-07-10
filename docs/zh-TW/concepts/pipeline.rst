CoT pipeline
============

Pipeline 對一份 code diff 跑一連串 *review steps*\ 。每個 step 產生一段
markdown；後續 step 可以從共用的 ``ReviewContext`` 讀前面的輸出。預設
registry 有五個 step──這條五步鏈是完整（deep 層）的行為；加上
``--step-plan adaptive`` 時會逐檔裁剪（見下文）。逐檔模式會多開一個
輸出結構化 finding 的 step。

Step 順序
---------

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Step
     - 它產出什麼
   * - ``first_summary``
     - 第一輪 PR summary──改了什麼、為什麼、有哪些風險。
   * - ``first_code_review``
     - 對 diff 做的 free-form review，依據 global rules。
   * - ``linter``
     - 只看 style / formatting 問題。
   * - ``code_smell``
     - 可維護性與設計層面的疑慮。
   * - ``total_summary``
     - 整合：讀前面四個輸出加 diff，給出最終判斷與合併建議。
   * - ``inline_findings``
     - *(僅 per-file)* 輸出 ``{line, severity, comment, suggestion?}``
       的 JSON 陣列，由 runner 轉成 GitHub inline review comment。

前五個由 ``build_global_rule_template`` 包起來，讓 RAG 規則與 per-repo
規則以一致的方式注入。\ ``inline_findings`` 跳過這個 wrap，這樣模型比較
可能輸出純 JSON。所有 prompt 模板隨套件內附於 ``prthinker/prompts/``\ ，
逐位元組鏡射自正典的 ``codes/run/CoT_Prompts/`` 語料。

另有三個只在降階審查深度時使用的 prompt-backed step（見下一節）：

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Step
     - 它產出什麼
   * - ``compact_review``
     - 整條分析鏈的單呼叫替代品──一個 prompt 涵蓋正確性、lint 層級
       問題、code smell 與簡短結論，取代五次模型呼叫。
   * - ``unified_review``
     - **一次**\ 模型呼叫同時產出 findings JSON、簡短分析摘要與判定；
       pipeline 會把 payload 拆回歷史沿用的 ``inline_findings`` /
       ``compact_review`` result key。
   * - ``batch_findings``
     - trivial 檔案的多檔合批 prompt：多個小 diff 併成一次呼叫審查，
       回傳的扁平 findings 陣列依 ``path`` 標籤拆回逐檔 finding。

自適應 step 規劃（``--step-plan adaptive``）
--------------------------------------------

預設（``--step-plan full``）每個檔案都跑所有已設定的 step。加上
``--step-plan adaptive`` 時，一個純函數、確定性的規劃器
（``prthinker.step_planner``）會為每個 ``FileDiff`` 指派四個深度層級
之一，只看 diff 本身（大小、檔案種類）加上 pipeline 本來就會算的
逐檔風險分。風險優先於大小：對歷史上脆弱的檔案做三行改動絕不算
trivial。

skip
   機器產生的檔案──lockfile（``package-lock.json``\ 、
   ``poetry.lock`` 等）、minified bundle、產生的 artifact、
   ``vendor/`` / ``node_modules/`` 這類 vendored 目錄──以及純空白
   的重排版。零模型呼叫、零檢索，但檔案仍會出現在總結中並標為
   skipped，讓「依政策跳過」看得見而非無聲消失。

trivial
   文件／宣告式設定副檔名（``.md``\ 、\ ``.rst``\ 、\ ``.json``\ 、
   ``.yaml``\ 、\ ``.toml`` 等）或至多 5 行變更。只留下產出輸出的
   step（inline findings、walkthrough）。整份計畫只剩 findings pass
   的 trivial 檔案會\ **合批**\ ：每次模型呼叫最多 6 個檔案／24 000
   字元的 diff，走 ``batch_findings`` prompt。回傳陣列依 ``path``
   標籤拆回逐檔，經過與單檔審查完全相同的驗證解析器，且每個檔案的
   findings 各自獨立快取，differential review 仍逐檔生效。

standard
   介於兩者之間的一切。一次 ``unified_review`` 呼叫回傳 findings
   JSON 加簡短摘要與判定，拆回歷史沿用的 ``inline_findings`` /
   ``compact_review`` result key，因此 findings 解析、報告、gate
   全部不變。加上 ``--counterfactual``\ （它消費解析後的 findings）
   時，standard 層改為保留兩次呼叫的 ``compact_review`` +
   ``inline_findings`` 形態。

deep
   變更 200 行以上，或風險分 ≥ 0.7──風險覆寫不論大小或檔案種類都
   生效。保留完整五步鏈加上所有已設定的額外 step。

降階層級同時也會壓低生成上限：trivial 為 4096 個新 token、standard
為 8192；deep 維持 pipeline 全域預算。所選層級會記錄在每個檔案的
``step_outputs`` 之 ``step_plan`` key，隨審查結果進入序列化輸出與
報告，深度決策全程可稽核。

兩種執行模式
------------

Single-pass
   對整份 diff 跑一個 prompt sweep。便宜，但模型只看得到 file headers，
   不容易說「是哪一行」有問題。沒有 inline review。

Per-file
   Diff 被切成一個個 ``FileDiff``\ ，pipeline 對每個檔跑一次，每跑可以追加
   ``InlineFindingsStep`` 來產 per-line 的 ``InlineFinding``\ 。Runner 聚合
   結果，套用 dismissed filter，發 GitHub review。

Per-file 是 production 設定；內附的 GHA workflow 預設開啟。

Diff 解析
---------

``prthinker.diff.parse_unified_diff`` 把 unified diff 切成 ``FileDiff``
物件，並追蹤每個檔在 *新邊* 出現過的 line numbers。這份集合驅動 line
驗證：任何 ``InlineFinding`` 指向不在 diff 內的行都會在送到 GitHub 前就
被丟掉。GitHub 本來就會拒絕針對被刪除行的留言，先在 client 側丟乾淨可以
讓 review API 呼叫更乾淨。

Findings extraction
-------------------

``inline_findings`` step 要求模型輸出 JSON 陣列。
``prthinker.findings`` 的解析器刻意做得寬容：

1. 剝掉 Markdown fenced-code 包裝（\ ``\`\`\`json … \`\`\```\ ）。
2. 找最外層的 ``[ ... ]`` 區塊。
3. 用 ``json.loads`` 解；失敗就退回 per-object regex。
4. 每筆對 ``InlineFinding`` Pydantic schema 做驗證──丟掉格式錯的。
5. ``line`` 不在該檔 diff lines 內的也丟掉。
6. *sanitize* ``suggestion`` 欄位：丟掉建議但保留 textual comment，當以下
   任一條件成立：

   * severity 為 ``info``\ （prompt 禁止對 info 級別給 suggestion）。
   * ``start_line > line``\ 。
   * 多行 suggestion 的行數對不上 range。
   * ``start_line`` 不在 diff 內。

錯的 suggestion 比沒有 suggestion 更糟（reviewer 可能盲目套用），所以保留
門檻設得高。

Dismissed filter
----------------

解析後，可選的 ``DismissedFilter`` 會把 comment 文本與既有 dismissed 範例
太相似的 finding 丟掉。store 的 schema 請見 :doc:`corpora`。

輸出通道
--------

每個 PR 上 reviewer 會寫三個通道：

* **總結留言**\ ──一條 PR conversation 留言，靠 sentinel marker upsert，
  讓重跑時不會洗版。Per-file 模式下每個檔案會渲染成可摺疊的
  ``<details>`` 區塊。
* **Inline review**\ ──一筆 ``POST /pulls/:n/reviews``\ ，每個倖存 finding
  各自一條留言。Suggestion 區塊在 GitHub UI 上會渲染成一鍵 *Apply
  suggestion* 按鈕。
* **Check Run**\ ──開始時開成 ``in_progress``\ ，根據 ``--gate-on`` 與 surviving
  findings 結算為 ``success`` 或 ``failure``\ 。
