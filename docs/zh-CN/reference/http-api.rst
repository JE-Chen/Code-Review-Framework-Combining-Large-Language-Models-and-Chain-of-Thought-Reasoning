HTTP API
========

确定性扩展端点
--------------

``POST /evaluation/retrieval`` 接受 ``retrieved``\ 、\ ``expected``\ 、
``used`` 与 ``cited_correct`` 数组。\ ``POST /attestation/review`` 返回
一份未签名的 in-toto review statement。两个端点都不执行仓库代码，
验证仍是 runner 端 sandbox 的责任。

``codes/run/fastapi_server.py`` 的 FastAPI server 提供一组同步端点
（\ ``/healthz``\ 、\ ``/ask``\ 、\ ``/rag``\ 、\ ``/review``\ ）以及与之
对应的 job-pattern 端点（\ ``/review/{submit,result,cancel}`` 和
``/ask/{submit,result,cancel}``\ ）。

只有 job-pattern 端点适合放在有 HTTP idle timeout 的 reverse proxy
后面。Cloudflare 免费 / Pro / Business 方案把单一 request 上限砍在
100 秒，但 30B MoE backend 跑一个 per-file review 要好几分钟、
跑 PR-wide overall summary 合成要十几分钟──任何同步呼叫穿过
proxy 都会被砍掉。改用 submit/poll 后每一个 HTTP round-trip 都在
一秒内完成，worker 则在 server 端跑到收尾。

Server 端有一个常驻 sweeper thread 每 30 秒巡所有 job 表，任何
running job 若 result endpoint 超过 180 秒没被 poll 就自动 set
``cancel_event``──避免 GHA runner 被取消后 backend 仍在白烧 GPU
跑没人读的 review（见下方 cancel endpoint）。

两张 job 表都有上限（\ ``PRTHINKER_MAX_JOBS``\ ，默认每类 32）：先淘汰
已终止的 job，当每个 slot 都被进行中的 job 占住时，submit 端点返回
``503``\ ──等一个 poll 间隔后重试即可。请求在触到 GPU 之前也会先做
预算检查：prompt 超过 ``PRTHINKER_MAX_INPUT_TOKENS``\ （默认 16384），
或 ``max_new_tokens`` 超过 ``PRTHINKER_MAX_NEW_TOKENS``\ （默认
32768），都会在边界快速失败，而不是在生成中途以一个难以理解的
CUDA OOM 浮现。

所有请求都支持可选的 ``Authorization: Bearer <token>`` header。Server 本身
不校验 token──如果需要实际的身份验证，请套在 reverse proxy（nginx、
Cloudflare Access 之类）后面。

GET /healthz
------------

存活探针。

**Response 200**

.. code-block:: json

   {"status": "ok", "model": "Qwen/Qwen3-Coder-30B-A3B-Instruct"}

GET /metrics
------------

Prometheus exposition endpoint。安装 ``prometheus-fastapi-instrumentator``
时启用（未安装则服务器记录一笔 log 并跳过），导出各 endpoint 的请求数、
延迟 histogram（p50 / p95 / p99 panel 之来源）与 HTTP 状态计数。除了这些
transport 指标,服务器在同一 endpoint 另外输出 review 领域指标——
``prthinker_reviews_total``\ （依 ``mode``\ 、\ ``outcome``\ ）、
``prthinker_review_duration_seconds``\ 、\ ``prthinker_review_findings``\
与 ``prthinker_reviews_in_progress``\ ——所以每跑完一次审查都会留下数据点,
与 HTTP 流量无关。与其他路径一样\ **不做认证**\ ——monitoring overlay 之
nginx 在内网 docker network 上 scrape；未经 reverse-proxy ACL 请勿对外
公开。

**Response 200**\ ：Prometheus 文本 exposition 格式之 ``text/plain``\ 。

POST /ask
---------

单次文本生成。为向后兼容保留──新集成建议用下面更高层的 endpoint。

**Request body**\ （\ ``AskRequest``\ ）：

.. code-block:: json

   {
     "prompt": "...",
     "max_new_tokens": 32768
   }

**Response 200**\ ：\ ``text/plain``\ ，内容为生成文本。

POST /rag
---------

对查询取回 RAG 规则。

**Request body**\ （\ ``RagRequest``\ ）：

.. code-block:: json

   {
     "query": "diff 或任意文本",
     "threshold": 0.7,
     "k": 15
   }

**Response 200**\ （\ ``RagResponse``\ ）：

.. code-block:: json

   {
     "docs": ["rule text 1", "rule text 2"]
   }

POST /review
------------

在服务器端完整跑 CoT pipeline。\ ``prthinker review-pr --use-remote-pipeline``
就是打这个。

**Request body**\ （\ ``ReviewRequest``\ ）：

.. code-block:: json

   {
     "code_diff": "diff --git a/foo.py b/foo.py\n...",
     "file_path": "foo.py",
     "steps": null,
     "rag_enabled": true,
     "rag_threshold": 0.7,
     "max_new_tokens": 32768,
     "extra_rules": ["Always use Path.resolve", "..."]
   }

字段语义：

* ``file_path``\ ──设值时表示这是单个文件的 diff，服务器会追加
  ``InlineFindingsStep``\ ，响应中会带 parsed ``inline_findings``\ 。
  ``null`` 时对整份 diff blob 跑五步 pipeline，\ ``inline_findings`` 为 ``[]``\ 。
* ``steps``\ ──可选的明确 step 列表。\ ``null`` 代表用 declaration order 跑全部
  已注册的 step。
* ``extra_rules``\ ──per-repo 团队规则，接在 RAG 检索规则之后。

**Response 200**\ （\ ``ReviewResponse``\ ）：

.. code-block:: json

   {
     "code_diff": "...",
     "rag_docs": ["...", "..."],
     "steps": [
       {"name": "first_summary", "output": "..."},
       {"name": "first_code_review", "output": "..."},
       {"name": "linter", "output": "..."},
       {"name": "code_smell", "output": "..."},
       {"name": "total_summary", "output": "..."},
       {"name": "inline_findings", "output": "[...]"}
     ],
     "inline_findings": [
       {
         "path": "foo.py",
         "line": 12,
         "severity": "warning",
         "comment": "用 logging 取代 print。",
         "suggestion": "    logger.info('hello')",
         "original": "    print('hello')",
         "start_line": null
       }
     ]
   }

服务器端（通过 ``PRTHINKER_DISMISSED_PATH`` 设置的）dismissed filter 在响应送出
之前就会跑完，所以与既有 dismissal 相似的 finding 不会出现在这份响应中。

**错误**

* ``400``\ ──``code_diff`` 为空。
* ``422``\ ──payload 过不了 Pydantic 校验。
* ``500``\ ──生成或 RAG 失败。服务器端有 log；client 应以 backoff 重试。

POST /review/submit
-------------------

``/review`` 的异步对应 endpoint，立即返回 job id，server 端用 daemon
thread 跑 CoT pipeline。任何 client 与 server 之间经过 100 秒 idle
timeout 之 proxy（Cloudflare 免费 / Pro / Business 方案）都应改用
这条，同步 ``/review`` 必死于 504。

**Request body** (``ReviewRequest``)──与 ``/review`` 一致。

**Response 200** (``ReviewJobSubmitResponse``):

.. code-block:: json

   {"job_id": "fa3d996466ee4666baae72b842d3b149"}

Job 存于 process-local dict，TTL 1 小时；server 重启即丢。

GET /review/result/{job_id}
---------------------------

轮询已 submit 之 job 结果。Client 应以短间隔（如 5 秒）调用──
每次 round-trip 都很快，不会触发 proxy idle timeout。整体等待
由 client 自己的 deadline 决定。

**Response 200** (``ReviewJobStatusResponse``):

.. code-block:: json

   {
     "job_id": "fa3d996466ee4666baae72b842d3b149",
     "status": "running",
     "result": null,
     "error": null
   }

``status`` 可能的值:

* ``pending``\ ──已 submit 但 worker thread 还没开始。
* ``running``\ ──worker thread 正在 ``_execute_review`` 中。
* ``done``\ ──``result`` 为 ``/review`` 对应的 ``ReviewResponse``\ 。
* ``error``\ ──``error`` 为 ``"<ExceptionClass>: <msg>"``\ 。
  Client 应直接呈现；除非根本原因（OOM、模型加载失败等）解决
  否则重试无用。
* ``cancelled``\ ──worker 被 ``/review/cancel`` 或 idle sweeper 中断。
  属 terminal；client 应视同失败并停止 poll。

每次成功 poll 都会更新 job 的 ``last_polled_at`` heartbeat，正在
poll 的 client 永远不会触发 idle sweeper。

**错误**

* ``404``\ ──未知 ``job_id``\ （或已过 TTL 被回收）。

POST /review/cancel/{job_id}
----------------------------

标记 running review job 取消。Client 端 try/finally 与 workflow
的取消处理器都会调用它，让被中止的 CI run 不会在 backend 继续
烧 GPU。

**Response 200**:

.. code-block:: json

   {"job_id": "...", "cancelled": true, "status": "running"}

Endpoint 设 worker 的 ``cancel_event``\ ；pipeline 在 step 边界
检查它，local backend 的 ``StoppingCriteria`` 在 ``model.generate``
每 decode 一个 token 就 poll 一次，所以正在跑的 step 约 100 ms 内
就会返回。Terminal job（\ ``done`` / ``error`` / ``cancelled``\ ）
返回 ``{"cancelled": false, "status": "<current>"}`` 不动。

**错误**

* ``404``\ ──未知 ``job_id``\ 。

POST /ask/submit
----------------

``/ask`` 的 job-pattern 对应 endpoint。任何需要超过 proxy timeout
的单一 prompt 生成都应改用这条（例如 aggregate 之 PR-wide overall
summary 合成，默认 ``max_new_tokens=16784``\ ）。

**Request body** (``AskRequest``)──与 ``/ask`` 一致。

**Response 200** (``AskJobSubmitResponse``):

.. code-block:: json

   {"job_id": "924c5daea164453f91f7a91feb57fb4c"}

GET /ask/result/{job_id}
------------------------

轮询已 submit 之 ``/ask`` job 结果。Status 语义与
``GET /review/result/{job_id}`` 相同；``status`` 为 ``done`` 时
``result`` 为生成出的纯文本。

**Response 200** (``AskJobStatusResponse``):

.. code-block:: json

   {
     "job_id": "924c5daea164453f91f7a91feb57fb4c",
     "status": "done",
     "result": "<生成文本>",
     "error": null
   }

POST /ask/cancel/{job_id}
-------------------------

标记 running ask job 取消。与 ``/review/cancel`` 同契约──设
worker 的 ``cancel_event``\ ，local backend 的 ``StoppingCriteria``
在下一个 token 中断生成。

Schema 定义
-----------

:mod:`prthinker.schemas` 内的 Pydantic 模型是 wire format 的单一真实
来源。服务器（FastAPI 的 ``response_model``\ ）与 runner
（\ ``model_validate_json``\ ）都引用它，type drift 不可能发生。

.. autoclass:: prthinker.schemas.AskRequest
   :noindex:

.. autoclass:: prthinker.schemas.RagRequest
   :noindex:

.. autoclass:: prthinker.schemas.RagResponse
   :noindex:

.. autoclass:: prthinker.schemas.ReviewRequest
   :noindex:

.. autoclass:: prthinker.schemas.ReviewResponse
   :noindex:

.. autoclass:: prthinker.schemas.ReviewJobSubmitResponse
   :noindex:

.. autoclass:: prthinker.schemas.ReviewJobStatusResponse
   :noindex:

.. autoclass:: prthinker.schemas.AskJobSubmitResponse
   :noindex:

.. autoclass:: prthinker.schemas.AskJobStatusResponse
   :noindex:

.. autoclass:: prthinker.schemas.InlineFinding
   :noindex:

.. autoclass:: prthinker.schemas.StepOutput
   :noindex:
