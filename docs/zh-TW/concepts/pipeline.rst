CoT pipeline
============

Pipeline 對一份 code diff 跑一連串固定的 *review steps*\ 。每個 step 產生一段
markdown；後續 step 可以從共用的 ``ReviewContext`` 讀前面的輸出。預設
registry 有五個 step；逐檔模式會多開一個輸出結構化 finding 的 step。

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

前五個住在 ``codes/run/CoT_Prompts/``\ ，由 ``build_global_rule_template``
包起來，讓 RAG 規則與 per-repo 規則以一致的方式注入。\ ``inline_findings``
跳過這個 wrap，這樣模型比較可能輸出純 JSON。

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

``reviewmind.diff.parse_unified_diff`` 把 unified diff 切成 ``FileDiff``
物件，並追蹤每個檔在 *新邊* 出現過的 line numbers。這份集合驅動 line
驗證：任何 ``InlineFinding`` 指向不在 diff 內的行都會在送到 GitHub 前就
被丟掉。GitHub 本來就會拒絕針對被刪除行的留言，先在 client 側丟乾淨可以
讓 review API 呼叫更乾淨。

Findings extraction
-------------------

``inline_findings`` step 要求模型輸出 JSON 陣列。
``reviewmind.findings`` 的解析器刻意做得寬容：

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
