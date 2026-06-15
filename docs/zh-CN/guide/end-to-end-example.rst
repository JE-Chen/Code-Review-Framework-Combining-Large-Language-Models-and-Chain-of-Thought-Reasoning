端到端示例
==========

一份把 prthinker 所有组件串成一条完整流程之走查\ ：GPU 推理服务器、
驱动它的 runner（CLI 或 GitHub Actions）、以及对同一台服务器发起
脚本级审查的 Python API\ 。

.. contents::
   :local:
   :depth: 2


场景设定
--------

Solo developer 拥有一台 GPU 机器（≥ 18 GB VRAM）\ 。在 GPU host 跑
4-bit NF4 量化的 ``Qwen3-Coder-30B-A3B-Instruct``\ ；GitHub Actions
在每个 PR 打开时自动审查\ ；偶尔从本地 Python 脚本对某份 diff 跑一次性
审查\ 。


Step 1 — 推理服务器（GPU host）
--------------------------------

两条等价路径：最小化用 ``uvicorn``\ ，或用 ``docker compose``\ （默认
跑在 ``:9000`` HTTP；若正式部署需 TLS + bearer token，可叠用下面的
overlay\ ）\ 。

1a. uvicorn
~~~~~~~~~~~

.. code-block:: bash

   # 在 GPU 机器上
   git clone https://github.com/<your-org>/prthinker.git
   cd prthinker
   pip install -e ".[server]"             # torch / transformers / faiss / fastapi

   # 学习语料（可选；空文件即可，服务器在 len == 0 时会忽略）
   mkdir -p .prthinker && touch \
       .prthinker/dismissed.jsonl \
       .prthinker/accepted.jsonl

   # 启动（模型在 import time 载入；首次需下载权重）
   export HF_HOME=/srv/hf-cache
   export PRTHINKER_DISMISSED_PATH=$PWD/.prthinker/dismissed.jsonl
   export PRTHINKER_ACCEPTED_PATH=$PWD/.prthinker/accepted.jsonl
   export PRTHINKER_CACHE_ENABLED=true
   export PRTHINKER_TELEMETRY_ENABLED=true

   uvicorn codes.run.fastapi_server:app \
       --host 0.0.0.0 --port 9000 --workers 1

``--workers 1`` 必要 —— 模型只该载入一份\ 。

默认模型为 ``Qwen/Qwen3-Coder-30B-A3B-Instruct``\ ，自动套用 4-bit NF4
+ double-quant + bf16 compute\ 。若 ``codes/train/outputs-lora-qwen3-coder-30b``
存在则会以 QLoRA 路径挂上 adapter\ ；否则只跑量化后之 base model\ 。

健康检查：

.. code-block:: bash

   curl http://localhost:9000/healthz
   # {"status":"ok","model":"Qwen/Qwen3-Coder-30B-A3B-Instruct"}


1b. Docker compose（默认 — HTTP on :9000）
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   cd prthinker/docker
   cp .env.example .env       # PRTHINKER_HOST_PORT 默认 9000
   docker compose -f docker-compose.server-qwen3-coder.yml up -d

   curl http://your-host:9000/healthz

可选：TLS + bearer token overlay
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

正式部署可叠上 ``docker-compose.tls.yml``\ ──加上 nginx 反向代理做 TLS
termination 与 bearer-token 闸门\ ，prthinker container 藏在它后面\ 。

.. code-block:: bash

   cd prthinker/docker
   # 编辑 .env：
   #   PRTHINKER_BACKEND_TOKEN=<长随机字符串>   # openssl rand -hex 32
   #   TLS_CERT_DIR=/etc/letsencrypt/live/your-host
   docker compose -f docker-compose.server-qwen3-coder.yml -f docker-compose.tls.yml up -d

   curl https://your-host/healthz \
       -H "Authorization: Bearer $PRTHINKER_BACKEND_TOKEN"


Step 2 — Runner
---------------

Runner 端不需要 GPU\ ，用 ``runner`` extra 即可\ 。

2a. 本地 CLI
~~~~~~~~~~~~

.. code-block:: bash

   pip install -e ".[runner]"             # 只装 httpx + pydantic

   git diff main..HEAD > my-change.diff

   # 指向自部署服务器 + 开启所有研究级扩展
   prthinker review-file my-change.diff \
       --backend remote \
       --remote-url https://your-host \
       --remote-api-key "$PRTHINKER_BACKEND_TOKEN" \
       --use-remote-pipeline \
       --per-file --inline-review \
       --counterfactual --provenance \
       --judge --self-correct \
       --max-findings-per-file 10


2b. GitHub Actions
~~~~~~~~~~~~~~~~~~

把 workflow 放到 ``.github/workflows/prthinker.yml``：

.. code-block:: yaml

   name: prthinker
   on:
     pull_request:
       types: [opened, synchronize, reopened]

   permissions:
     contents: read
     pull-requests: write
     checks: write
     actions: read

   concurrency:
     group: prthinker-${{ github.event.pull_request.number }}
     cancel-in-progress: true

   jobs:
     prthinker:
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
         - name: Run prthinker
           env:
             GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
             GITHUB_REPOSITORY: ${{ github.repository }}
             PRTHINKER_PR_NUMBER: ${{ github.event.pull_request.number }}

             # Backend —— 指向 Step 1 那台服务器
             PRTHINKER_BACKEND: remote
             PRTHINKER_REMOTE_URL: ${{ secrets.PRTHINKER_BACKEND_URL }}
             PRTHINKER_REMOTE_API_KEY: ${{ secrets.PRTHINKER_BACKEND_API_KEY }}
             PRTHINKER_USE_REMOTE_PIPELINE: "true"

             # 五步 CoT + 逐文件 inline review
             PRTHINKER_PER_FILE: "true"
             PRTHINKER_INLINE_REVIEW: "true"
             PRTHINKER_MAX_FINDINGS_PER_FILE: "10"

             # RAG over 全局 + per-repo 规则
             PRTHINKER_RAG_ENABLED: "true"
             PRTHINKER_REMOTE_RAG: "true"
             PRTHINKER_RULES_DIR: ./team-rules

             # 合并前 gate：出现 error 严重度 finding 就 Check Run failure
             PRTHINKER_GATE_ON: "error"

             # CI 失败 log 前置到 diff（grounded review）
             PRTHINKER_INCLUDE_CI_SIGNALS: "true"

             # 研究级扩展（opt-in；均需搭配 --inline-review）
             PRTHINKER_REPLY_TO_AUTHOR: "true"
             PRTHINKER_COUNTERFACTUAL: "true"
             PRTHINKER_PROVENANCE: "true"
             PRTHINKER_JUDGE: "true"
             PRTHINKER_SELF_CORRECT: "true"
           run: python -m prthinker review-pr

Repo Settings → Secrets → Actions 设两个 secrets：

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Secret
     - Value
   * - ``PRTHINKER_BACKEND_URL``
     - ``https://your-host``\ （docker 路径）或
       ``http://your-host:9000``\ （uvicorn 路径）
   * - ``PRTHINKER_BACKEND_API_KEY``
     - Step 1b 设的 ``PRTHINKER_BACKEND_TOKEN``\ ；走 uvicorn 路径可空\ 。


Step 3 — Python API
-------------------

想把 prthinker 嵌入自家工具（IDE plugin、Slack bot、批量扫 repo）\ ，
直接驱动 pipeline：

.. code-block:: python

   # review_a_diff.py
   from pathlib import Path

   from prthinker.backends.remote import RemoteHttpBackend
   from prthinker.config import RemoteBackendConfig
   from prthinker.pipeline import CoTPipeline, PerFileReviewOptions
   from prthinker.rag import RemoteRAGRetriever


   def review_diff(diff_text: str, *, backend_url: str, token: str) -> dict:
       """跑完整 CoT pipeline，返回适合丢给 UI 的 dict。"""
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
               PerFileReviewOptions(
                   inline_review=True,
                   counterfactual=True,
                   provenance=True,
                   judge=True,
                   self_correct=True,
                   max_findings_per_file=10,
               ),
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
           backend_url=os.environ["PRTHINKER_REMOTE_URL"],
           token=os.environ.get("PRTHINKER_REMOTE_API_KEY", ""),
       )
       json.dump(out, sys.stdout, indent=2, ensure_ascii=False)


跑法：

.. code-block:: bash

   git diff main..HEAD > my.diff
   export PRTHINKER_REMOTE_URL=https://your-host
   export PRTHINKER_REMOTE_API_KEY=...
   python review_a_diff.py my.diff > result.json


流程一览
--------

.. code-block:: text

   ┌────────────────────────────────────────────────────────────────────┐
   │ Step 1: GPU host                                                   │
   │   uvicorn   ◄──  /healthz  /ask  /rag  /review                     │
   │   ├ Qwen3-Coder-30B-A3B-Instruct (4-bit NF4 + double-quant)        │
   │   ├ 可选 LoRA adapter (codes/train/outputs-lora-…)                 │
   │   └ 全局规则 FAISS index                                           │
   └─────────────────────────────▲──────────────────────────────────────┘
                                 │ HTTPS + Bearer
            ┌────────────────────┼────────────────────┐
            │                    │                    │
   ┌────────┴───────┐  ┌─────────┴─────────┐  ┌──────┴──────────┐
   │ Step 2a CLI    │  │ Step 2b GHA       │  │ Step 3 Python   │
   │ review-file    │  │ review-pr → PR    │  │ API → JSON 给   │
   │ stdout         │  │ 评论 + Check Run  │  │ 自家 UI         │
   └────────────────┘  └───────────────────┘  └─────────────────┘

三条路径共用同一台服务器、同一个模型、同一份学习语料 —— 跑哪一条
只是\ *runner*\ 的差别\ 。
