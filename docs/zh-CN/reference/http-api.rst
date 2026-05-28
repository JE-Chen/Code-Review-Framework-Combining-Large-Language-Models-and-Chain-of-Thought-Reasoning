HTTP API
========

``codes/run/fastapi_server.py`` 的 FastAPI server 提供四个 endpoint。
``/ask`` 为了向后兼容返回 plain text，其他都收发 JSON。

所有请求都支持可选的 ``Authorization: Bearer <token>`` header。Server 本身
不校验 token──如果需要实际的身份验证，请套在 reverse proxy（nginx、
Cloudflare Access 之类）后面。

GET /healthz
------------

存活探针。

**Response 200**

.. code-block:: json

   {"status": "ok", "model": "Qwen/Qwen3-Coder-30B-A3B-Instruct"}

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

.. autoclass:: prthinker.schemas.InlineFinding
   :noindex:

.. autoclass:: prthinker.schemas.StepOutput
   :noindex:
