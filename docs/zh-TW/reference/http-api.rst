HTTP API
========

確定性擴充端點
--------------

``POST /evaluation/retrieval`` 接受 ``retrieved``\ 、\ ``expected``\ 、
``used`` 與 ``cited_correct`` 陣列。\ ``POST /attestation/review`` 回傳
一份未簽章的 in-toto review statement。兩個端點都不執行儲存庫程式碼，
驗證仍是 runner 端 sandbox 的責任。

``codes/run/fastapi_server.py`` 的 FastAPI server 提供一組同步端點
（\ ``/healthz``\ 、\ ``/ask``\ 、\ ``/rag``\ 、\ ``/review``\ ）以及一組
與之對應的 job-pattern 端點（\ ``/review/{submit,result,cancel}`` 和
``/ask/{submit,result,cancel}``\ ）。

只有 job-pattern 端點適合放在有 HTTP idle timeout 的 reverse proxy
後面。Cloudflare 免費 / Pro / Business 方案把單一 request 上限砍在
100 秒，但 30B MoE backend 跑一個 per-file review 要好幾分鐘、
跑 PR-wide overall summary 合成要十幾分鐘──任何同步呼叫穿過
proxy 都會被砍掉。改用 submit/poll 後每一個 HTTP round-trip 都在
一秒內完成，worker 則於 server 端跑到收尾。

Server 端有一個常駐 sweeper thread 每 30 秒巡所有 job 表，任何
running job 若 result endpoint 超過 180 秒沒被 poll 就自動 set
``cancel_event``──避免 GHA runner 被取消後 backend 仍在白燒 GPU
跑沒人讀的 review（見下方 cancel endpoint）。

兩個 job 表都有上限（\ ``PRTHINKER_MAX_JOBS``\ ，每種預設 32）：
已終止的 job 先被淘汰；當所有 slot 都是進行中的 job 時，submit
endpoint 回 ``503``\ ──隔一個 poll 間隔再重試即可。請求在碰到 GPU
之前也會先過預算檢查：prompt 超過 ``PRTHINKER_MAX_INPUT_TOKENS``
（預設 16384）、或 ``max_new_tokens`` 超過 ``PRTHINKER_MAX_NEW_TOKENS``
（預設 32768），都會在邊界快速失敗，而不是在生成途中冒出一個難以
解讀的 CUDA OOM。

所有請求都支援可選的 ``Authorization: Bearer <token>`` header。Server 本身
不驗 token──如果需要實際的身分驗證，請套在 reverse proxy（nginx、
Cloudflare Access 之類）後面。

GET /healthz
------------

存活探針\ ，且會實際觸碰 CUDA context：在每張 GPU 上跑一次微小的
matmul（若當下有 generation 持有 GPU lock 則不阻塞\ 、直接跳過 ——
正在生成的 GPU 本身就證明是活的）\ 。\ ``gpu`` 回報
``ok`` / ``busy`` / ``no-cuda``\ 。

**Response 200**

.. code-block:: json

   {"status": "ok", "model": "Qwen/Qwen3-Coder-30B-A3B-Instruct", "gpu": "ok"}

**Response 503** —— 探測失敗：CUDA context 不健康（CI 的 preflight
ping 會視為不可達\ ，優雅跳過整個 review matrix）\ 。若探測失敗屬於
*中毒* context（致命 CUDA / cuBLAS / cuDNN 錯誤）\ ，行程會直接退出\ ，
讓容器的 supervisor 重啟一個乾淨的行程\ ；任何 generation job 死於
此類錯誤時同樣 fail-fast\ 。設 ``PRTHINKER_NO_CUDA_FAILFAST=1``
可保留舊的繼續服務行為\ 。

GET /metrics
------------

Prometheus exposition endpoint。安裝 ``prometheus-fastapi-instrumentator``
時啟用（未安裝則伺服器記錄一筆 log 並略過），匯出各 endpoint 的請求數、
延遲 histogram（p50 / p95 / p99 panel 之來源）與 HTTP 狀態計數。除了這些
transport 指標,伺服器在同一 endpoint 另外輸出 review 領域指標——
``prthinker_reviews_total``\ （依 ``mode``\ 、\ ``outcome``\ ）、
``prthinker_review_duration_seconds``\ 、\ ``prthinker_review_findings``\
與 ``prthinker_reviews_in_progress``\ ——所以每跑完一次審查都會留下資料點,
與 HTTP 流量無關。與其他路徑一樣\ **不做驗證**\ ——monitoring overlay 之
nginx 在內網 docker network 上 scrape；未經 reverse-proxy ACL 請勿對外
公開。

**Response 200**\ ：Prometheus 文字 exposition 格式之 ``text/plain``\ 。

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
     "extra_rules": ["Always use Path.resolve", "..."],
     "step_plan": "full"
   }

欄位語義：

* ``file_path``\ ──設值時表示這是單一檔案的 diff，伺服器會追加
  ``InlineFindingsStep``\ ，回應中會帶 parsed ``inline_findings``\ 。
  ``null`` 時對整份 diff blob 跑已設定的 step 鏈，\ ``inline_findings`` 為 ``[]``\ 。
* ``steps``\ ──可選的明確 step 清單。\ ``null`` 代表用 declaration order 跑全部
  已註冊的 step。
* ``extra_rules``\ ──per-repo 團隊規則，接在 RAG 檢索規則之後。
* ``step_plan``\ ──逐檔審查深度政策，於 ``file_path`` 設值時生效：
  ``"full"``\ （預設）跑完所有已設定的 step；\ ``"adaptive"`` 對該檔
  做深度規劃（見 CLI 的 ``--step-plan``\ ），選定的 tier 會以
  ``steps`` 中一筆 ``step_plan`` 項目回報。可選且向後相容：早於此
  欄位的伺服器會忽略它，伺服器把任何未知值視同 ``"full"``\ 。

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

POST /review/submit
-------------------

``/review`` 的非同步對應 endpoint，立即回 job id，server 端用 daemon
thread 跑 CoT pipeline。任何 client 與 server 之間經過 100 秒 idle
timeout 之 proxy（Cloudflare 免費 / Pro / Business 方案）都應改用
這條，同步 ``/review`` 必死於 504。

**Request body** (``ReviewRequest``)──與 ``/review`` 一致。

**Response 200** (``ReviewJobSubmitResponse``):

.. code-block:: json

   {"job_id": "fa3d996466ee4666baae72b842d3b149"}

Job 存於 process-local dict，TTL 1 小時；server 重啟即丟。

GET /review/result/{job_id}
---------------------------

輪詢已 submit 之 job 結果。Client 應以短間隔（如 5 秒）呼叫──
每次 round-trip 都很快，不會觸發 proxy idle timeout。整體等待
由 client 自己的 deadline 決定。

**Response 200** (``ReviewJobStatusResponse``):

.. code-block:: json

   {
     "job_id": "fa3d996466ee4666baae72b842d3b149",
     "status": "running",
     "result": null,
     "error": null
   }

``status`` 可能的值:

* ``pending``\ ──已 submit 但 worker thread 還沒開始。
* ``running``\ ──worker thread 正在 ``_execute_review`` 中。
* ``done``\ ──``result`` 為 ``/review`` 對應的 ``ReviewResponse``\ 。
* ``error``\ ──``error`` 為 ``"<ExceptionClass>: <msg>"``\ 。
  Client 應直接呈現；除非根本原因（OOM、模型載入失敗等）解決
  否則重試無用。
* ``cancelled``\ ──worker 被 ``/review/cancel`` 或 idle sweeper 中
  斷。屬 terminal；client 應視同失敗並停止 poll。

每次成功 poll 都會更新 job 的 ``last_polled_at`` heartbeat，正在
poll 的 client 永遠不會觸發 idle sweeper。

**錯誤**

* ``404``\ ──未知 ``job_id``\ （或已過 TTL 被回收）。

POST /review/cancel/{job_id}
----------------------------

標記 running review job 取消。Client 端 try/finally 與 workflow
的取消處理器都會呼叫它，讓被中止的 CI run 不會在 backend 繼續
燒 GPU。

**Response 200**:

.. code-block:: json

   {"job_id": "...", "cancelled": true, "status": "running"}

Endpoint 設 worker 的 ``cancel_event``\ ；pipeline 於 step 邊界
檢查它，local backend 的 ``StoppingCriteria`` 在 ``model.generate``
每 decode 一個 token 就 poll 一次，所以正在跑的 step 約 100 ms 內
就會返回。Terminal job（\ ``done`` / ``error`` / ``cancelled``\ ）
回 ``{"cancelled": false, "status": "<current>"}`` 不動。

**錯誤**

* ``404``\ ──未知 ``job_id``\ 。

POST /ask/submit
----------------

``/ask`` 的 job-pattern 對應 endpoint。任何需要超過 proxy timeout
的單一 prompt 生成都應改用這條（例如 aggregate 之 PR-wide overall
summary 合成，預設 ``max_new_tokens=16784``\ ）。

**Request body** (``AskRequest``)──與 ``/ask`` 一致。

**Response 200** (``AskJobSubmitResponse``):

.. code-block:: json

   {"job_id": "924c5daea164453f91f7a91feb57fb4c"}

GET /ask/result/{job_id}
------------------------

輪詢已 submit 之 ``/ask`` job 結果。Status 語義與
``GET /review/result/{job_id}`` 相同；``status`` 為 ``done`` 時
``result`` 為生成出的純文字。

**Response 200** (``AskJobStatusResponse``):

.. code-block:: json

   {
     "job_id": "924c5daea164453f91f7a91feb57fb4c",
     "status": "done",
     "result": "<生成文字>",
     "error": null
   }

POST /ask/cancel/{job_id}
-------------------------

標記 running ask job 取消。與 ``/review/cancel`` 同合約──設
worker 的 ``cancel_event``\ ，local backend 的 ``StoppingCriteria``
於下一個 token 中斷生成。

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
