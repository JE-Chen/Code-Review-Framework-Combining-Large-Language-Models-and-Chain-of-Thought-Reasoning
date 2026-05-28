Judge step 与 streaming
=======================

两个建立在 per-file 模式之上的可选功能。

Judge step（\ ``--judge``\ ）
-----------------------------

启用时，每个 per-file pipeline 在末尾会多跑一个 step：``JudgeStep`` 读
该文件的 ``total_summary`` 与已 parse 的 ``inline_findings``\ ，输出一段
JSON：

.. code-block:: text

   {
     "verdict": "approve" | "request_changes" | "comment",
     "score":   0-10,
     "reasons": ["短 bullet", ...]
   }

Parser 刻意做得宽容（与 inline findings parser 同样的态度），模型输出
格式偏离时会 fallback 到安全的 ``comment``\ 默认，而不是让整个 review 崩掉。

跨文件聚合
~~~~~~~~~~

各文件的 verdict 用保守规则合并成单一 PR 级决策：

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - 各文件组合
     - PR 级 verdict
   * - 任何一文件 ``request_changes``
     - ``request_changes``
   * - 全部 ``approve``
     - ``approve``
   * - 其他情况
     - ``comment``

再对应到 GitHub Review API 的 ``event``\ ：

* ``approve`` → ``APPROVE``
* ``request_changes`` → ``REQUEST_CHANGES``
* ``comment`` → ``COMMENT``\ （默认）

所以 ``--inline-review --judge --gate-on error`` 一起开时，PR 上会：

1. 贴每个 inline finding（含 suggestion 区块）。
2. 根据 judge 把 review 的 event 设为 approve / request changes /
   comment。
3. Check Run gate 用同一份 findings 独立判断。

Gate 与 judge 是两个独立信号──gate 是机械式（数 error finding），judge
是诠释式。同一个 PR 上两者可以同时触发。

对 paper 的 ablation
~~~~~~~~~~~~~~~~~~~~

Backend 是 per-process 选的，所以你可以让 judge step 跑在与 review 不同
的 backend 上（例如：五步 CoT 跑本地 Qwen、judge 跑 Anthropic Claude）。
Schema 在 :class:`prthinker.schemas.JudgeVerdict`\ ；parser 与 aggregator
在 :mod:`prthinker.judge`\ 。

Streaming（\ ``--stream``\ ）
-----------------------------

长 review（5+ steps × per-file × per-PR）会跑好几分钟；不开 streaming
时 CLI 在跑完之前完全没输出。\ ``--stream`` 会让每个 backend call 走
incremental 路径：

* **OpenAI-compat backend**\ ──请求加 ``stream: true``\ ，解析 SSE
  ``data:`` 事件，逐块 yield ``choices[0].delta.content``\ 。
  ``last_usage`` 从最后一个含 ``stream_options: include_usage`` 的事件取。
* **Anthropic backend**\ ──请求加 ``stream: true``\ ，从
  ``content_block_delta`` 事件 yield 文本、从 ``message_start`` 取
  ``input_tokens``\ 、从 ``message_delta`` 取 ``output_tokens``\ 。
* **本地与自部署 remote backend**\ ──fallback 到 base class 默认行为：把
  ``generate()`` 全文当成一块 yield 出来。没有真正的 streaming 收益，但
  caller 不必特别分支。

Chunk 写到 ``stderr``\ ，不会污染送进 stdout 的最终 PR 评论。每个 step
切换时打印 ``[step_name :: file_path]`` 作 header。
``CachingBackend`` 命中时短路成单一块，\ ``InstrumentedBackend`` 在 stream
结束时记录 latency / tokens──cache 与 telemetry 在开不开 stream 下行为
一致。

权衡
~~~~

* Streaming 每个 backend call 多一次握手，但拿到可见进度。
* 慢线时的感知延迟从「等 3 分钟」变「两秒看到第一个 token」。
* 部分 OpenAI-compat 服务器（较旧版 vLLM、某些 llama.cpp build）不支持
  ``stream_options.include_usage``\ ，streaming 响应没有 ``usage`` block──
  这些 call 的 telemetry 会 fallback 到 char-count 估算。
