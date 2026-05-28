HTTP API
========

``codes/run/fastapi_server.py`` 的 FastAPI server 提供四個 endpoint。
``/ask`` 為了向後相容回 plain text，其他都收發 JSON。

所有請求都支援可選的 ``Authorization: Bearer <token>`` header。Server 本身
不驗 token──如果需要實際的身分驗證，請套在 reverse proxy（nginx、
Cloudflare Access 之類）後面。

GET /healthz
------------

存活探針。

**Response 200**

.. code-block:: json

   {"status": "ok", "model": "Qwen/Qwen3-Coder-30B-A3B-Instruct"}

POST /ask
---------

單次文字生成。為向後相容保留──新整合建議用下面更高階的 endpoint。

**Request body**\ （\ ``AskRequest``\ ）：

.. code-block:: json

   {
     "prompt": "...",
     "max_new_tokens": 32768
   }

**Response 200**\ ：\ ``text/plain``\ ，內容為生成文字。

POST /rag
---------

對查詢取回 RAG 規則。

**Request body**\ （\ ``RagRequest``\ ）：

.. code-block:: json

   {
     "query": "diff 或任意文字",
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

在伺服器端完整跑 CoT pipeline。\ ``prthinker review-pr --use-remote-pipeline``
就是打這個。

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

欄位語義：

* ``file_path``\ ──設值時表示這是單一檔案的 diff，伺服器會追加
  ``InlineFindingsStep``\ ，回應中會帶 parsed ``inline_findings``\ 。
  ``null`` 時對整份 diff blob 跑五步 pipeline，\ ``inline_findings`` 為 ``[]``\ 。
* ``steps``\ ──可選的明確 step 清單。\ ``null`` 代表用 declaration order 跑全部
  已註冊的 step。
* ``extra_rules``\ ──per-repo 團隊規則，接在 RAG 檢索規則之後。

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

伺服器端（透過 ``PRTHINKER_DISMISSED_PATH`` 設定的）dismissed filter 在回應送出
之前就會跑完，所以與既有 dismissal 相似的 finding 不會出現在這份回應中。

**錯誤**

* ``400``\ ──``code_diff`` 為空。
* ``422``\ ──payload 通不過 Pydantic 驗證。
* ``500``\ ──生成或 RAG 失敗。伺服器端有 log；client 應以 backoff 重試。

Schema 定義
-----------

:mod:`prthinker.schemas` 內的 Pydantic 模型是 wire format 的單一真實
來源。伺服器（FastAPI 的 ``response_model``\ ）與 runner
（\ ``model_validate_json``\ ）都引用它，type drift 不可能發生。

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
