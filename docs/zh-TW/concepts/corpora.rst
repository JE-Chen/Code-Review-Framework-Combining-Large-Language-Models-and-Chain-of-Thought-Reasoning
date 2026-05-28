學習語料：dismissed 與 accepted
====================================

Reviewer 維護兩份 JSONL store，捕捉 PR 作者長期對 finding 的反應。兩者都由
``harvest-*`` CLI 指令產生，並在伺服器啟動時被讀入。

不對稱的角色
------------

.. list-table::
   :header-rows: 1
   :widths: 25 35 40

   * - Store
     - 用途
     - 訊號來源
   * - ``dismissed.jsonl``
     - *過濾* 候選 finding（太相似就丟掉）
     - 👎 reaction、「false positive」回覆、被忽略的留言
   * - ``accepted.jsonl``
     - *補強* prompt（top-K 範例注入）
     - 含 ``Apply suggestion`` commit 的 PR

這個不對稱是刻意的。Dismissal 是負向訓練訊號（\ *下次別再產出像這樣的東西*\ ），
所以做成基於相似度的輸出過濾。Accepted suggestion 是正向訓練訊號
（\ *這種建議在這個 repo 有效*\ ），所以以 in-context exemplar 形式在 prompt
建立時注入。

Store schema
------------

``dismissed.jsonl``\ ──每行一個 JSON object：

.. code-block:: json

   {
     "path": "src/auth.py",
     "comment": "別把 token 用明文存",
     "reason": "thumbs-down reaction",
     "diff_snippet": "@@ -3,1 +3,3 @@\n+token = req.json()['token']"
   }

``accepted.jsonl``\ ──每行一個 JSON object：

.. code-block:: json

   {
     "path": "src/auth.py",
     "comment": "用 Path.resolve 把路徑正規化",
     "suggestion": "    path = Path(path).resolve()",
     "pr_number": 137
   }

兩者都是 append-only──harvest 指令絕不覆蓋既有行，所以 ``--max-prs 100``
跑完再用 ``--max-prs 200`` 跑一次是安全的。讀不過 JSON 的行會被 warning
略過。

Harvest
-------

.. code-block:: bash

   # 抓 👎 與 dismissal-keyword reply
   reviewmind harvest-dismissed \
       --repo owner/name \
       --max-prs 100 \
       --out .reviewmind/dismissed.jsonl

   # 掃含「Apply suggestion」commit 的 PR，
   # 把那些 PR 上有 ```suggestion``` 區塊的留言全部保留
   reviewmind harvest-accepted \
       --repo owner/name \
       --max-prs 100 \
       --out .reviewmind/accepted.jsonl

Dismissal 關鍵字 list 目前是寫死的（混合英文與繁體中文）：\ *false positive、
wontfix、not relevant、ignore this、intentional、by design*\ ，外加「誤判」、
「不是問題」、「不修」、「已討論」、「故意」、「預期」、「本來就是」等。

Accepted 收集是 best-effort：GitHub 不會把「Apply suggestion」commit 反查
連到產出它的 review comment，所以 harvester 假設在含此 commit 的 PR 上，
任何附 ``suggestion`` 區塊的留言都被採納了。誤收的部分在 K=3 時會被沖淡。

相似度過濾（dismissed）
-----------------------

伺服器端 ``DismissedFilter`` 在 boot 時對每筆 stored ``comment`` 各 embed
一次，使用與 RAG 同一支 ``codes/util/faiss_util.get_embedding``\ 。對每個
候選 finding，filter 會 embed finding 的 ``comment`` 文本，跟所有 stored
範例算 cosine。Finding 被丟掉的條件：

.. math::

   \max_{e \in \text{store}} \langle \mathrm{emb}(f.\text{comment}),
   \mathrm{emb}(e.\text{comment}) \rangle \geq \tau

預設 ``τ = 0.85``\ 。可透過 ``REVIEWMIND_DISMISSED_THRESHOLD`` 覆寫。

Top-K 範例（accepted）
----------------------

``AcceptedExamplesRetriever`` 邏輯一樣，但回傳超過自己（較低）閾值的前 K
個結果，而不是過濾。被選中的範例會渲染進 ``inline_findings`` prompt 的
``## Examples of past advice that was accepted in this repo`` 區塊，位置
在 diff 本身之前。

預設：\ ``K = 3``\ 、\ ``τ = 0.6``\ 。可透過 ``REVIEWMIND_ACCEPTED_TOP_K``\ 、
``REVIEWMIND_ACCEPTED_THRESHOLD`` 覆寫。

冷啟動
------

兩個過濾器在 store 為空或缺檔時都是 no-op──啟動 log 會顯示
``filter disabled`` / ``exemplars disabled``\ 。沒有 store 也能正常跑 reviewer
多久都行；語料是品質加成，不是必要依賴。

研究用途
--------

這兩個檔案是從 production review 流量中累積出來的標註負例 + 正例語料。
可以用來衡量：

* 各類 finding 隨時間變化的 dismissal rate
* 相似度過濾的丟棄率（對 held-out 人工標註集計算 precision / recall）
* Exemplar 注入是否能改變產出 suggestion 的分佈

原始稿件中的對應數字請見 ``paper/``\ 。
