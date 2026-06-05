Secret 過濾與 MCP 整合
======================

兩個彼此無關的擴充，但共享同一個動機：讓 prthinker 在原本的 GHA workflow
之外也安全、便利。

Secret redaction（\ ``--redact-secrets``\ ）
--------------------------------------------

Backend 接到付費第三方 API（OpenAI、Anthropic …）時，PR diff 內可能夾帶
被 ``.gitignore`` 漏掉的真實 secret──diff 顯示出 ``.env`` 內容、test
fixture 寫死的 token、snapshot test 內的 JWT。開 ``--redact-secrets``
（env ``PRTHINKER_REDACT_SECRETS=true``\ ）後，runner 會在送出任何 backend
call 前對 diff 做 pre-pass，把已知的 secret pattern 換成
``<REDACTED:<kind>>``\ 。

涵蓋的 pattern
~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - kind
     - 對應
   * - ``private-key``
     - PEM ``-----BEGIN ... PRIVATE KEY-----`` 整塊
   * - ``github-token``
     - ``ghp_`` / ``gho_`` / ``ghu_`` / ``ghs_`` / ``ghr_`` PAT
   * - ``anthropic-key``
     - ``sk-ant-…``
   * - ``openai-key``
     - ``sk-…`` 與 ``sk-proj-…``\ （排除 Anthropic 前綴）
   * - ``stripe-key``
     - ``sk_live_…`` / ``sk_test_…`` / ``rk_live_…`` / ``rk_test_…``
   * - ``aws-access-key-id``
     - ``AKIA`` / ``ASIA`` / ``AIDA`` / ``AROA`` / ``AGPA`` / ``ANPA`` / ``ANVA``
   * - ``slack-token``
     - ``xoxa-`` / ``xoxb-`` / ``xoxp-`` / ``xoxr-`` / ``xoxs-``
   * - ``gcp-api-key``
     - ``AIza…``\ （39 字元）
   * - ``twilio-sid``
     - ``AC`` 加 32 個 hex
   * - ``jwt``
     - 三段 base64url 用 ``.`` 串接，header 起頭 ``eyJ``

偵測規則刻意保守──code review 出現誤判是雜訊但可修；漏判則是 secret 真的
洩漏出去。

設計性質
~~~~~~~~

* **Idempotent。**\ 已 redacted 過的 diff 再餵一次是 no-op──
  ``<REDACTED:...>`` 不會被自己當成 secret。
* **對 cache 友善。**\ Redaction 在 prompt 組裝與 cache key 計算之前跑，
  所以同一個 PR 跑兩次仍然能命中同一份 cache，不管有沒有 secret 被換掉。
* **會 log、不會洩漏。**\ ``RedactionReport`` 只統計各 kind 的命中次數，
  從不包含內容，CI log 上線安全。

什麼時候不要開
~~~~~~~~~~~~~~

* Backend 是本機 HF backend 或自架 FastAPI（跟 repo 同網段）時，redaction
  只有形式上的意義──secret 並沒有要去哪。關掉可以讓 diff 看起來原樣。
* 接付費第三方 backend 時，請當成必選。

Model Context Protocol 整合
---------------------------

Model Context Protocol（MCP）是讓 LLM client（Claude Desktop、Cursor、
Continue、Cline、Zed …）呼叫外部 tool 的開放標準。prthinker 內附一個
MCP server 適配器，任何 MCP client 都能在 IDE 內直接驅動 review──不必
透過 GHA。

安裝
~~~~

.. code-block:: bash

   pip install -e ".[mcp]"

這會在 runner extras 之上多裝 ``mcp`` SDK。

暴露的 tool
~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - tool name
     - 做什麼
   * - ``review_diff``
     - 對 unified diff 字串跑完整 CoT pipeline，回傳跟 PR 留言一樣的
       markdown body。\ ``redact_secrets`` 預設 ``True``\ 。
   * - ``triage_diff``
     - 對 unified diff 字串跑無需模型的靜態訊號（不呼叫 backend）：衝突標記、
       Trojan-Source 字元、吞錯、重新命名、刪除、mode 變更、大段貼上、純格式
       變更、覆蓋缺口、殘留 debug 與延遲工作標記。瞬間且免費;\
       ``redact_secrets`` 預設 ``True``\ 。輸出同 ``triage`` CLI 指令\ 。
   * - ``stats``
     - 對本機 telemetry SQLite 在指定時間區間做聚合，回 markdown 表。
       適合「這週 review 燒了多少」這類提問。

設定
~~~~

Backend 選擇用同一組 ``PRTHINKER_*`` env var；密鑰只在 env，不會落到
MCP server 自己的 config 內。

Claude Desktop 設定範例（macOS 路徑：
``~/Library/Application Support/Claude/claude_desktop_config.json``\ ）：

.. code-block:: json

   {
     "mcpServers": {
       "prthinker": {
         "command": "prthinker",
         "args": ["mcp"],
         "env": {
           "PRTHINKER_BACKEND": "anthropic",
           "ANTHROPIC_API_KEY": "sk-ant-...",
           "PRTHINKER_ANTHROPIC_MODEL": "claude-sonnet-4-6",
           "PRTHINKER_CACHE_ENABLED": "true",
           "PRTHINKER_TELEMETRY_ENABLED": "true"
         }
       }
     }
   }

同樣的格式套到 Cursor、Continue、Cline、Zed 也行──請參考各 client 的
MCP 文件確認檔路徑。

典型 IDE 流程
~~~~~~~~~~~~~

1. 本地 stage 改動：\ ``git add -p``\ 。
2. 在 IDE 聊天視窗：\ *「Run prthinker on my staged diff」*\ 。
3. Client 的 LLM 呼叫 ``review_diff``\ ，參數是 ``$(git diff --cached)``\ 。
4. Markdown review 串流回 chat panel；使用者直接決定要不要採納建議。

這對不想為了拿 review 而走完 PR + GHA 的個人開發者是 killer feature。

權衡
~~~~

* MCP 模式預設關掉 RAG（用 ``NoOpRetriever``\ ）。在 stdio 子行程內載入
  FAISS 太重、embedding 模型也很少裝在使用者筆電──需要 RAG 時請改用
  ``PRTHINKER_BACKEND=remote`` 讓 FastAPI server 負責檢索。
* MCP server 在跨呼叫間是 stateless 的；cache 與 telemetry store 跨呼叫
  仍持久存在，所以 cost visibility 一樣有效。
