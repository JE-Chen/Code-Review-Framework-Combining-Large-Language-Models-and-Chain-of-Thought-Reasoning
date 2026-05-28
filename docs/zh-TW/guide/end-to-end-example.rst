端到端範例
==========

一份把 reviewmind 所有元件串成一條完整流程之走查\ ：GPU 推論伺服器、
驅動它的 runner（CLI 或 GitHub Actions）、以及對同一台伺服器發起
腳本級審查的 Python API\ 。

.. contents::
   :local:
   :depth: 2


情境設定
--------

Solo developer 擁有一台 GPU 機器（≥ 18 GB VRAM）\ 。在 GPU host 跑
4-bit NF4 量化的 ``Qwen3-Coder-30B-A3B-Instruct``\ ；GitHub Actions
在每個 PR 開起時自動審查\ ；偶爾從本機 Python 腳本對某份 diff 跑一次性
審查\ 。


Step 1 — 推論伺服器（GPU host）
--------------------------------

兩條等價路徑：最小化用 ``uvicorn``\ ，或為正式部署用 ``docker compose``
加上 nginx TLS 與 bearer token 閘門\ 。

1a. uvicorn
~~~~~~~~~~~

.. code-block:: bash

   # 在 GPU 機器上
   git clone https://github.com/<your-org>/reviewmind.git
   cd reviewmind
   pip install -e ".[server]"             # torch / transformers / faiss / fastapi

   # 學習語料（可選；空檔即可，伺服器在 len == 0 時會忽略）
   mkdir -p .reviewmind && touch \
       .reviewmind/dismissed.jsonl \
       .reviewmind/accepted.jsonl

   # 啟動（模型在 import time 載入；首次需下載權重）
   export HF_HOME=/srv/hf-cache
   export REVIEWMIND_DISMISSED_PATH=$PWD/.reviewmind/dismissed.jsonl
   export REVIEWMIND_ACCEPTED_PATH=$PWD/.reviewmind/accepted.jsonl
   export REVIEWMIND_CACHE_ENABLED=true
   export REVIEWMIND_TELEMETRY_ENABLED=true

   uvicorn codes.run.fastapi_server:app \
       --host 0.0.0.0 --port 8000 --workers 1

``--workers 1`` 必要 —— 模型只該載入一份\ 。

預設模型為 ``Qwen/Qwen3-Coder-30B-A3B-Instruct``\ ，自動套用 4-bit NF4
+ double-quant + bf16 compute\ 。若 ``codes/train/outputs-lora-qwen3-coder-30b``
存在則會以 QLoRA 路徑掛上 adapter\ ；否則只跑量化後之 base model\ 。

健檢：

.. code-block:: bash

   curl http://localhost:8000/healthz
   # {"status":"ok","model":"Qwen/Qwen3-Coder-30B-A3B-Instruct"}


1b. Docker compose + nginx + bearer token
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   cd reviewmind/docker
   cp .env.example .env
   # 編輯 .env：
   #   REVIEWMIND_BACKEND_TOKEN=<長隨機字串>
   #   TLS_CERT_DIR=/etc/letsencrypt/live/your-host
   docker compose up -d

   curl https://your-host/healthz \
       -H "Authorization: Bearer $REVIEWMIND_BACKEND_TOKEN"


Step 2 — Runner
---------------

Runner 端不需要 GPU\ ，用 ``runner`` extra 即可\ 。

2a. 本機 CLI
~~~~~~~~~~~~

.. code-block:: bash

   pip install -e ".[runner]"             # 只裝 httpx + pydantic

   git diff main..HEAD > my-change.diff

   # 指向自架伺服器 + 開啟所有研究級擴充
   reviewmind review-file my-change.diff \
       --backend remote \
       --remote-url https://your-host \
       --remote-api-key "$REVIEWMIND_BACKEND_TOKEN" \
       --use-remote-pipeline \
       --per-file --inline-review \
       --counterfactual --provenance \
       --judge --self-correct \
       --max-findings-per-file 10


2b. GitHub Actions
~~~~~~~~~~~~~~~~~~

把 workflow 放到 ``.github/workflows/reviewmind.yml``：

.. code-block:: yaml

   name: ReviewMind
   on:
     pull_request:
       types: [opened, synchronize, reopened]

   permissions:
     contents: read
     pull-requests: write
     checks: write
     actions: read

   concurrency:
     group: reviewmind-${{ github.event.pull_request.number }}
     cancel-in-progress: true

   jobs:
     reviewmind:
       runs-on: ubuntu-latest
       if: ${{ github.event.pull_request.draft == false }}
       timeout-minutes: 30
       steps:
         - uses: actions/checkout@v4
           with:
             ref: ${{ github.event.pull_request.head.sha }}
             fetch-depth: 1
         - uses: actions/setup-python@v5
           with:
             python-version: "3.12"
             cache: "pip"
         - name: Install runner deps
           run: pip install -e ".[runner]"
         - name: Run ReviewMind
           env:
             GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
             GITHUB_REPOSITORY: ${{ github.repository }}
             REVIEWMIND_PR_NUMBER: ${{ github.event.pull_request.number }}

             # Backend —— 指向 Step 1 那台伺服器
             REVIEWMIND_BACKEND: remote
             REVIEWMIND_REMOTE_URL: ${{ secrets.REVIEWMIND_BACKEND_URL }}
             REVIEWMIND_REMOTE_API_KEY: ${{ secrets.REVIEWMIND_BACKEND_API_KEY }}
             REVIEWMIND_USE_REMOTE_PIPELINE: "true"

             # 五步 CoT + 逐檔 inline review
             REVIEWMIND_PER_FILE: "true"
             REVIEWMIND_INLINE_REVIEW: "true"
             REVIEWMIND_MAX_FINDINGS_PER_FILE: "10"

             # RAG over 全域 + per-repo 規則
             REVIEWMIND_RAG_ENABLED: "true"
             REVIEWMIND_REMOTE_RAG: "true"
             REVIEWMIND_RULES_DIR: ./team-rules

             # 合併前 gate：出現 error 嚴重度 finding 就 Check Run failure
             REVIEWMIND_GATE_ON: "error"

             # CI 失敗 log 前置到 diff（grounded review）
             REVIEWMIND_INCLUDE_CI_SIGNALS: "true"

             # 研究級擴充（opt-in；皆需搭配 --inline-review）
             REVIEWMIND_REPLY_TO_AUTHOR: "true"
             REVIEWMIND_COUNTERFACTUAL: "true"
             REVIEWMIND_PROVENANCE: "true"
             REVIEWMIND_JUDGE: "true"
             REVIEWMIND_SELF_CORRECT: "true"
           run: python -m reviewmind review-pr

Repo Settings → Secrets → Actions 設兩個 secrets：

==============================  ===================================================
Secret                          Value
==============================  ===================================================
``REVIEWMIND_BACKEND_URL``      ``https://your-host``\ （docker 路徑）或
                                ``http://your-host:8000``\ （uvicorn 路徑）
``REVIEWMIND_BACKEND_API_KEY``  Step 1b 設的 ``REVIEWMIND_BACKEND_TOKEN``\ ；
                                走 uvicorn 路徑可空\ 。
==============================  ===================================================


Step 3 — Python API
-------------------

想把 reviewmind 嵌進自家工具（IDE plugin、Slack bot、批次掃 repo）\ ，
直接驅動 pipeline：

.. code-block:: python

   # review_a_diff.py
   from pathlib import Path

   from reviewmind.backends.remote import RemoteHttpBackend
   from reviewmind.config import RemoteBackendConfig
   from reviewmind.pipeline import CoTPipeline
   from reviewmind.rag import RemoteRAGRetriever


   def review_diff(diff_text: str, *, backend_url: str, token: str) -> dict:
       """跑完整 CoT pipeline，回傳適合丟給 UI 的 dict。"""
       backend = RemoteHttpBackend(
           RemoteBackendConfig(url=backend_url, api_key=token)
       )
       retriever = RemoteRAGRetriever(
           base_url=backend_url, api_key=token, threshold=0.7,
       )
       pipeline = CoTPipeline(backend=backend, retriever=retriever)

       try:
           result = pipeline.run_per_file(
               diff_text,
               inline_review=True,
               counterfactual=True,
               provenance=True,
               judge=True,
               self_correct=True,
               max_findings_per_file=10,
           )
       finally:
           backend.close()
           retriever.close()

       return {
           "files": [
               {
                   "path": fr.path,
                   "summary": fr.total_summary,
                   "verdict": fr.verdict.verdict if fr.verdict else None,
                   "findings": [
                       {
                           "line": f.line,
                           "severity": f.severity,
                           "comment": f.comment,
                           "suggestion": f.suggestion,
                           "provenance": (
                               f.provenance.model_dump()
                               if f.provenance else None
                           ),
                       }
                       for f in fr.inline_findings
                   ],
                   "counterfactuals": [
                       cf.model_dump() for cf in fr.counterfactuals
                   ],
               }
               for fr in result.per_file
           ],
       }


   if __name__ == "__main__":
       import json, os, sys
       diff = Path(sys.argv[1]).read_text(encoding="utf-8")
       out = review_diff(
           diff,
           backend_url=os.environ["REVIEWMIND_REMOTE_URL"],
           token=os.environ.get("REVIEWMIND_REMOTE_API_KEY", ""),
       )
       json.dump(out, sys.stdout, indent=2, ensure_ascii=False)


跑法：

.. code-block:: bash

   git diff main..HEAD > my.diff
   export REVIEWMIND_REMOTE_URL=https://your-host
   export REVIEWMIND_REMOTE_API_KEY=...
   python review_a_diff.py my.diff > result.json


流程一覽
--------

.. code-block:: text

   ┌────────────────────────────────────────────────────────────────────┐
   │ Step 1: GPU host                                                   │
   │   uvicorn   ◄──  /healthz  /ask  /rag  /review                     │
   │   ├ Qwen3-Coder-30B-A3B-Instruct (4-bit NF4 + double-quant)        │
   │   ├ 可選 LoRA adapter (codes/train/outputs-lora-…)                 │
   │   └ 全域規則 FAISS index                                           │
   └─────────────────────────────▲──────────────────────────────────────┘
                                 │ HTTPS + Bearer
            ┌────────────────────┼────────────────────┐
            │                    │                    │
   ┌────────┴───────┐  ┌─────────┴─────────┐  ┌──────┴──────────┐
   │ Step 2a CLI    │  │ Step 2b GHA       │  │ Step 3 Python   │
   │ review-file    │  │ review-pr → PR    │  │ API → JSON 給   │
   │ stdout         │  │ 留言 + Check Run  │  │ 自家 UI         │
   └────────────────┘  └───────────────────┘  └─────────────────┘

三條路徑共用同一台伺服器、同一個模型、同一份學習語料 —— 跑哪一條
只是\ *runner*\ 的差別\ 。
