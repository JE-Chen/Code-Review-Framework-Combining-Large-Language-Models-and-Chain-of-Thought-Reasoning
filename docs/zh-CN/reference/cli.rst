CLI 参考
========

CLI 可通过已安装的 entry point 或 module 两种方式调用::

   reviewmind <subcommand> [options]
   python -m reviewmind <subcommand> [options]

全局选项
--------

.. option:: --log-level {DEBUG,INFO,WARNING,ERROR}

   默认 ``INFO``\ 。可用 ``REVIEWMIND_LOG_LEVEL`` 覆盖。

review-pr
---------

抓 PR diff、跑 pipeline、贴评论 + review + gate。

.. code-block:: text

   reviewmind review-pr
       --repo OWNER/NAME           # 或 $GITHUB_REPOSITORY
       --pr-number N
       --github-token TOKEN        # 或 $GITHUB_TOKEN
       [--backend {local,remote}]
       [--remote-url URL]
       [--use-remote-pipeline]
       [--no-rag] [--remote-rag] [--rag-threshold 0.7]
       [--rules-dir PATH]
       [--per-file] [--inline-review] [--max-findings-per-file 10]
       [--reply-to-author] [--counterfactual] [--provenance]
       [--judge] [--self-correct]
       [--gate-on {none,warning,error}]
       [--include-ci-signals] [--ci-signal-max-jobs 5] [--ci-signal-tail-chars 4000]
       [--marker '<!-- reviewmind:summary -->']
       [--dry-run]

值得注意的 flag：

* ``--dry-run``\ ──把总结评论打印到 stdout 而不贴上去，也跳过 Check Run。
* ``--marker``\ ──upsert PR 评论用的 sentinel HTML comment。只有同一个
  repo 想跑多个 reviewer 时才需要覆盖。

研究级 flag（opt-in\ ，需搭配 ``--inline-review``）：

.. option:: --reply-to-author

   读取 PR 作者对最近一则 reviewmind 摘要评论的回复\ ，并把它们以
   *Prior dialogue* 区块注入 inline-findings prompt\ 。\ 把对话回路
   闭上\ ，避免下一次审查静默重贴作者已回应过的评论\ 。环境变量：
   ``REVIEWMIND_REPLY_TO_AUTHOR``\ 。

.. option:: --counterfactual

   在 inline findings 之后\ ，跑一个 counterfactual / mutation step\ ，
   对属于\ *设计选择*\ 之评论列出竞争性实现方案与 trade-off 矩阵\ 。
   明确 bug / nit 之 finding 会被跳过\ 。每个文件多一次 backend 调用\ 。
   环境变量：``REVIEWMIND_COUNTERFACTUAL``\ 。

.. option:: --provenance

   要求模型对每条 finding 引用 RAG 规则 / accepted-example /
   diff 行号\ ，并在 PR 每个文件区块下加上\ *Audit trail*\ 摘要\ 。
   越界之引用会被静默丢弃\ ；坏引用绝不拖垮真评论\ 。环境变量：
   ``REVIEWMIND_PROVENANCE``\ 。

.. option:: --judge

   每文件自评步骤\ ，输出 ``approve`` / ``request_changes`` / ``comment``
   verdict\ 。CLI 跨文件聚合后映射为 GitHub review event\ 。

.. option:: --self-correct

   二次降噪：把存活之 findings 列给模型\ ，请它删掉它认为是噪音的条目\ 。
   每文件多一次 backend 调用\ 。安全失败方向：解析失败时保留原清单\ 。

review-file
-----------

对本地文件或 stdin 跑 pipeline。

.. code-block:: text

   reviewmind review-file PATH
       [--backend {local,remote}]
       [--remote-url URL] [--remote-api-key TOKEN]
       [--model-name NAME] [--lora-path PATH]
       [--no-rag] [--remote-rag] [--rag-threshold 0.7]
       [--rules-dir PATH]
       [--per-file] [--inline-review] [--max-findings-per-file 10]
       [--counterfactual] [--provenance] [--judge] [--self-correct]
       [--max-new-tokens 32768]
       [--steps a,b,c]
       [--output-dir PATH]

``PATH`` 可填 ``-`` 从 stdin 读 diff。

``--output-dir`` 会把每个 step 的原始输出增量写入磁盘──批量实验或调试
长跑时很有用。

``--steps`` 是逗号分隔的 step 名称列表；空（默认）就跑全部已注册的 step。

harvest-dismissed
-----------------

扫 PR review comment，把 dismissed finding 追加到 JSONL store。

.. code-block:: text

   reviewmind harvest-dismissed
       --repo OWNER/NAME
       --github-token TOKEN
       [--pr-number N | --max-prs 50]
       [--out .reviewmind/dismissed.jsonl]

设 ``--pr-number`` 时只扫那一个 PR；否则迭代最近 ``--max-prs`` 个依更新时间
排序的 closed PR。

harvest-accepted
----------------

扫 PR 看是否有应用过的 suggestion 区块，追加到 JSONL store。

.. code-block:: text

   reviewmind harvest-accepted
       --repo OWNER/NAME
       --github-token TOKEN
       [--pr-number N | --max-prs 50]
       [--out .reviewmind/accepted.jsonl]

当 PR 的任一 commit message 以 ``Apply suggestion(s) from code review`` 开头
时即视为「有采纳过建议」。该 PR 上每个带 ```suggestion``` 区块的评论都会
保留。

adversarial-eval
----------------

把 prompt-injection 语料丢给当前 backend\ ，将每一笔调用之结果写入
SQLite\ 。本子命令\ **不输出**\ 任何汇总检测率 —— 聚合计算交给下游 SQL\ ，
原始输出保留以利审计\ 。

.. code-block:: text

   reviewmind adversarial-eval
       --corpus PATH                # JSONL 语料（参考 seed.jsonl）
       --outcomes-path PATH         # SQLite 输出文件
       [--backend {local,remote,openai,anthropic}]
       [--remote-url URL] [--remote-api-key TOKEN]
       [--openai-model NAME] [--openai-api-key TOKEN]
       [--anthropic-model NAME] [--anthropic-api-key TOKEN]
       [--max-new-tokens 4096]

语料格式：每行一个 JSON 对象\ ，符合
:class:`reviewmind.adversarial.AttackCase`\ 。随附之
``reviewmind/adversarial_corpus/seed.jsonl`` 是手工撰写的种子\ ，
涵盖四种攻击类型（``direct_injection`` / ``encoded_payload`` /
``split_injection`` / ``role_hijack``）—— 它\ **不**\ 是 benchmark\ 。

outcomes 表 schema：

.. code-block:: sql

   CREATE TABLE outcomes (
     id          INTEGER PRIMARY KEY AUTOINCREMENT,
     timestamp   REAL    NOT NULL,
     case_id     TEXT    NOT NULL,
     category    TEXT    NOT NULL,
     backend     TEXT    NOT NULL,
     model       TEXT    NOT NULL,
     bypassed    INTEGER NOT NULL,   -- 0/1
     detected    INTEGER NOT NULL,   -- 0/1
     success_markers_hit   TEXT NOT NULL,  -- 逗号连接
     detection_markers_hit TEXT NOT NULL,
     output      TEXT    NOT NULL,
     error       TEXT
   );

Exit code
---------

* ``0``\ ──成功（含 dry-run 与零 finding 的情况）。
* ``1``\ ──runtime 失败（network、GPU、parse error）。\ ``--gate-on`` 启用时，
  Check Run 在传递错误前会被 PATCH 为 ``failure``\ 。
* ``2``\ ──argparse 参数解析或校验错误。
