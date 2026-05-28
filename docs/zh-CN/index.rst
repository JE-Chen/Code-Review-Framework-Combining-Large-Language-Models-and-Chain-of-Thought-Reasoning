reviewmind（简体中文）
========================

语言切换： `English <../../html-en/index.html>`_ ·
`繁體中文 <../../html-zh-TW/index.html>`_ ·
**简体中文**

为 GitHub Pull Request 设计的思维链（Chain-of-Thought）代码审查框架，
底层由微调后的 Qwen3-Coder 模型加上检索增强（RAG）提示驱动。

``reviewmind`` 会读取 PR diff、执行五步思维链审查、把结构化的总结与
一键应用的 ``suggestion`` 区块回帖到 PR。它会从每个 repo 的历史中学习──
被 PR 作者拒绝的评论下次会被过滤掉，被采纳的建议会以示例的形式注入
下一轮 prompt──并且可以充当合并前的必需状态检查。

你会得到什么
------------

* **五步 CoT pipeline**\ ──``first_summary`` → ``first_code_review`` →
  ``linter`` → ``code_smell`` → ``total_summary``\ ，外加可选的逐文件
  inline-findings 步骤，输出结构化 JSON。
* **逐文件 inline review**\ ，配合 GitHub ``suggestion`` 区块。
* **全局 RAG + 各 repo 规则包**\ ：通过 ``--rules-dir`` 注入团队规范。
* **两份学习语料**\ ：\ ``dismissed.jsonl``\ （过滤重复命中）与
  ``accepted.jsonl``\ （top-K 示例注入 prompt）。
* **CI 失败信号**\ 前置到 diff，提供 grounded review。
* **合并前 Check Run gate**\ ──可设为必需状态检查。
* **可替换 backend**\ ：本地 in-process Qwen + LoRA，或 HTTP 远程推理。

.. toctree::
   :maxdepth: 2
   :caption: 使用指南

   guide/installation
   guide/quickstart
   guide/github-actions
   guide/configuration
   guide/repo-config

.. toctree::
   :maxdepth: 2
   :caption: 概念

   concepts/architecture
   concepts/pipeline
   concepts/rag-and-rules
   concepts/corpora
   concepts/ci-and-gate
   concepts/cache-and-telemetry
   concepts/judge-and-streaming
   concepts/redaction-and-mcp
   concepts/hook-self-correct-auto-fix
   concepts/docker-platforms-report
   concepts/research-extensions

.. toctree::
   :maxdepth: 2
   :caption: 参考

   reference/cli
   reference/http-api
   reference/python-api

索引
----

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
