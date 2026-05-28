Judge step 與 streaming
=======================

兩個建構在 per-file 模式之上的選用功能。

Judge step（\ ``--judge``\ ）
-----------------------------

啟用時，每個 per-file pipeline 在結尾會多跑一個 step：``JudgeStep`` 讀
該檔的 ``total_summary`` 與已 parse 的 ``inline_findings``\ ，輸出一段
JSON：

.. code-block:: text

   {
     "verdict": "approve" | "request_changes" | "comment",
     "score":   0-10,
     "reasons": ["短 bullet", ...]
   }

Parser 刻意做得寬容（與 inline findings parser 同樣的態度），模型輸出
格式偏離時會 fallback 到安全的 ``comment``\ 預設，而不是讓整個 review 炸掉。

跨檔聚合
~~~~~~~~

各檔的 verdict 用保守規則合併成單一 PR 級決策：

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - 各檔組合
     - PR 級 verdict
   * - 任何一檔 ``request_changes``
     - ``request_changes``
   * - 全部 ``approve``
     - ``approve``
   * - 其他情況
     - ``comment``

再對應到 GitHub Review API 的 ``event``\ ：

* ``approve`` → ``APPROVE``
* ``request_changes`` → ``REQUEST_CHANGES``
* ``comment`` → ``COMMENT``\ （預設）

所以 ``--inline-review --judge --gate-on error`` 一起開時，PR 上會：

1. 貼每個 inline finding（含 suggestion 區塊）。
2. 根據 judge 把 review 的 event 設成 approve / request changes /
   comment。
3. Check Run gate 用同一份 findings 獨立判斷。

Gate 與 judge 是兩個獨立訊號──gate 是機械式（數 error finding），judge
是詮釋式。同一個 PR 上兩者可以同時觸發。

對 paper 的 ablation
~~~~~~~~~~~~~~~~~~~~

Backend 是 per-process 選的，所以你可以讓 judge step 跑在跟 review 不同
的 backend 上（例如：五步 CoT 跑本機 Qwen、judge 跑 Anthropic Claude）。
Schema 在 :class:`prthinker.schemas.JudgeVerdict`\ ；parser 與 aggregator
在 :mod:`prthinker.judge`\ 。

Streaming（\ ``--stream``\ ）
-----------------------------

長 review（5+ steps × per-file × per-PR）會跑好幾分鐘；不開 streaming
時 CLI 在跑完之前完全沒輸出。\ ``--stream`` 會讓每個 backend call 走
incremental 路徑：

* **OpenAI-compat backend**\ ──請求加 ``stream: true``\ ，解析 SSE
  ``data:`` 事件，逐塊 yield ``choices[0].delta.content``\ 。
  ``last_usage`` 從最後一個含 ``stream_options: include_usage`` 的事件抓。
* **Anthropic backend**\ ──請求加 ``stream: true``\ ，從
  ``content_block_delta`` 事件 yield 文字、從 ``message_start`` 抓
  ``input_tokens``\ 、從 ``message_delta`` 抓 ``output_tokens``\ 。
* **本機與自架 remote backend**\ ──fallback 到 base class 預設行為：把
  ``generate()`` 全文當成一塊 yield 出來。沒有真正的 streaming 收益，但
  caller 不必特別分支。

Chunk 寫到 ``stderr``\ ，不會污染送進 stdout 的最終 PR 留言。每個 step
切換時印 ``[step_name :: file_path]`` 作 header。
``CachingBackend`` 命中時短路成單一塊，\ ``InstrumentedBackend`` 在 stream
結束時記錄 latency / tokens──cache 與 telemetry 在開不開 stream 下行為
一致。

權衡
~~~~

* Streaming 每個 backend call 多一次握手，但拿到可見進度。
* 慢線時的感知延遲從「等 3 分鐘」變「兩秒看到第一個 token」。
* 部分 OpenAI-compat 伺服器（較舊版 vLLM、某些 llama.cpp build）不支援
  ``stream_options.include_usage``\ ，streaming 回應沒有 ``usage`` block──
  那些 call 的 telemetry 會 fallback 到 char-count 估算。
