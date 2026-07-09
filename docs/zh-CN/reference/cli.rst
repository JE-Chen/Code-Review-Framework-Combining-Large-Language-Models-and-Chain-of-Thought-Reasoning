CLI 参考
========

CLI 可通过已安装的 entry point 或 module 两种方式调用::

   prthinker <subcommand> [options]
   python -m prthinker <subcommand> [options]

全局选项
--------

.. option:: --log-level {DEBUG,INFO,WARNING,ERROR}

   默认 ``INFO``\ 。可用 ``PRTHINKER_LOG_LEVEL`` 覆盖。

review-pr
---------

抓 PR diff、跑 pipeline、贴评论 + review + gate。

.. code-block:: text

   prthinker review-pr
       --repo OWNER/NAME           # 或 $GITHUB_REPOSITORY
       --pr-number N
       --github-token TOKEN        # 或 $GITHUB_TOKEN
       [--backend {local,remote,openai,anthropic,gemini,cohere,mistral,claude-cli,codex-cli}]
       [--remote-url URL]
       [--use-remote-pipeline]
       [--no-rag] [--remote-rag] [--rag-threshold 0.7]
       [--rules-dir PATH]
       [--per-file] [--inline-review] [--max-findings-per-file 10]
       [--reply-to-author] [--counterfactual] [--provenance]
       [--diff-since-last] [--diff-cache-path PATH]
       [--verify-suggestions] [--verify-cmd CMD] [--verify-timeout 60] [--verify-workdir PATH]
       [--api-consistency] [--pr-classify] [--reproducibility-check]
       [--dep-upgrade-check]
       [--personas LIST] [--risk-weighted] [--risk-workdir PATH] [--diff-entropy]
       [--judge] [--self-correct]
       [--arbitration] [--arbitration-backends a,b]
       [--arbitration-strategy {majority,unanimous,any}]
       [--gate-on {none,warning,error}]
       [--include-ci-signals] [--ci-signal-max-jobs 5] [--ci-signal-tail-chars 4000]
       [--marker '<!-- prthinker:summary -->']
       [--dry-run]

值得注意的 flag：

* ``--dry-run``\ ──把总结评论打印到 stdout 而不贴上去，也跳过 Check Run。
* ``--marker``\ ──upsert PR 评论用的 sentinel HTML comment。只有同一个
  repo 想跑多个 reviewer 时才需要覆盖。
* ``--exclude-globs``\ ──逗号分隔之 fnmatch patterns；
  ``--per-file`` 模式下匹配任一 pattern 的 file 会被跳过。对 IDE
  配置、生成数据、大段 markdown 是便宜防线，不浪费 GPU 时间。Env:
  ``PRTHINKER_EXCLUDE_GLOBS``\ 。
* ``--target-file``\ ──设了之后，\ ``--per-file`` 模式只 review 这
  个 diff path，其它文件全跳过。让 CI matrix runner 各自接管一个
  file，给每个 file 自己的 timeout budget；matrix workflow 细节
  见 :doc:`../guide/github-actions`\ 。Env: ``PRTHINKER_TARGET_FILE``\ 。
* ``--output-json``\ ──把 partial ``ReviewResult`` 写成 JSON 而不
  post 到 GitHub。搭 matrix runner 的 ``--target-file``\ ，让每个
  shard 把自己 file 的 findings 收成 artifact，后面的 ``aggregate``
  job 才合一处理。Env: ``PRTHINKER_OUTPUT_JSON``\ 。

研究级 flag（opt-in\ ，需搭配 ``--inline-review``）：

.. option:: --reply-to-author

   读取 PR 作者对最近一则 prthinker 摘要评论的回复\ ，并把它们以
   *Prior dialogue* 区块注入 inline-findings prompt\ 。\ 把对话回路
   闭上\ ，避免下一次审查静默重贴作者已回应过的评论\ 。环境变量：
   ``PRTHINKER_REPLY_TO_AUTHOR``\ 。

.. option:: --counterfactual

   在 inline findings 之后\ ，跑一个 counterfactual / mutation step\ ，
   对属于\ *设计选择*\ 之评论列出竞争性实现方案与 trade-off 矩阵\ 。
   明确 bug / nit 之 finding 会被跳过\ 。每个文件多一次 backend 调用\ 。
   环境变量：``PRTHINKER_COUNTERFACTUAL``\ 。

.. option:: --provenance

   要求模型对每条 finding 引用 RAG 规则 / accepted-example /
   diff 行号\ ，并在 PR 每个文件区块下加上\ *Audit trail*\ 摘要\ 。
   越界之引用会被静默丢弃\ ；坏引用绝不拖垮真评论\ 。环境变量：
   ``PRTHINKER_PROVENANCE``\ 。

.. option:: --walkthrough

   新增一个每文件 ``WalkthroughStep``\ ，就该文件变更写出二至四句\
   「\ 做了什么、为何\ 」\ 的叙事\ ，钉于该文件区块最上方──为无推论之
   commit-message PR 概览之推论侧对应物\ 。它只描述（不评断）\ ，只依赖
   diff\ ，故开不开 ``--inline-review`` 皆可执行\ 。环境变量：
   ``PRTHINKER_WALKTHROUGH``\ 。

.. option:: --judge

   每文件自评步骤\ ，输出 ``approve`` / ``request_changes`` / ``comment``
   verdict\ 。CLI 跨文件聚合后映射为 GitHub review event\ 。

.. option:: --self-correct

   二次降噪：把存活之 findings 列给模型\ ，请它删掉它认为是噪音的条目\ 。
   每文件多一次 backend 调用\ 。安全失败方向：解析失败时保留原清单\ 。

.. option:: --diff-since-last

   把每文件之新侧内容 hash\ ，后续 push 时 hash 未变之文件直接 reuse
   上次 findings\ 。SQLite 存储体于 ``--diff-cache-path``（默认
   ``.prthinker/diff-cache.sqlite``），key 为
   ``(pr_number, repo, file_path, hunk_sha256)`` —— 跨 PR 隔离\ 。环境变量：
   ``PRTHINKER_DIFF_SINCE_LAST``\ 。

.. option:: --verify-suggestions

   把 working tree 复制到 disposable sandbox\ ，于 finding 之 line range
   套用 ``suggestion`` block\ ，再以 ``--verify-cmd``\（默认
   ``pytest -x``）于 ``--verify-timeout``\（默认 60s）下执行\ ，把每条
   finding 标 ``[verified]`` / ``[FAILED]`` / ``[skipped]`` /
   ``[error]``\ 。原 repo 绝不动\ 。环境变量：
   ``PRTHINKER_VERIFY_SUGGESTIONS``\ 。

.. option:: --api-consistency

   当 diff 同时碰到后端（``.py``）与前端（``.ts`` / ``.tsx`` /
   ``.js`` / ``.jsx``）\ ，新增一个 step 检测\ *跨文件*\ drift（重命名字段、
   移除路由、类型变更）\ 。单语言 PR 上静默 pass\ 。环境变量：
   ``PRTHINKER_API_CONSISTENCY``\ 。

.. option:: --pr-classify

   从 diff + 标题 + body 把 PR 分为 ``bugfix`` / ``feature`` /
   ``refactor`` / ``docs`` / ``chore`` / ``unknown``\ ，后续 review
   深度随之调整：docs PR 跳 inline findings\ ；bugfix PR 用 focused
   prompt + 较小 budget\ 。环境变量：``PRTHINKER_PR_CLASSIFY``\ 。

.. option:: --reproducibility-check

   同 prompt 跑两次 inline-findings step（非 0 temperature 自然产生
   第二样本）\ ，每条 finding 按跨 pass match 标 ``stable`` / ``low``\ 。
   后端通用 uncertainty proxy\ 。环境变量：
   ``PRTHINKER_REPRODUCIBILITY_CHECK``\ 。

.. option:: --dep-upgrade-check

   检测 lock-file（``requirements.txt`` / ``pyproject.toml`` /
   ``package.json``）中之版本 bump\ ，问模型该包之 breaking change
   是否影响本 repo 之实际用法\ 。环境变量：
   ``PRTHINKER_DEP_UPGRADE_CHECK``\ 。

.. option:: --personas <list>

   逗号分隔之 persona 名单（``security``\ 、``performance``\ 、
   ``readability``\ 、``api_stability``\ 、``maintainability``）── 或
   ``all`` 跑全 5 个\ 。每个 persona 之 prompt 限定模型只在该 lens 范围内
   评论\ ；之后一个 conflict-finder step 找出跨 persona 之分歧\ 。空（默认）
   即停用\ 。环境变量：``PRTHINKER_PERSONAS``\ 。

.. option:: --risk-weighted

   以 churn（``git log`` 于默认 90 天 lookback）\ 、complexity（HEAD 行数）\ 、
   bug history（commit message 命中 ``fix:`` / ``bug`` / ``revert``）算
   每文件风险分\ ；按分数线性缩放 ``max_findings_per_file`` 于 ``floor``
   （默认 2）到 ``ceiling``（默认 ``2 × base_budget``）之间\ 。
   ``--risk-workdir`` 指向 git repo\ 。另外会在总结中附一个可展开的
   「\ high-risk files\ 」\ 注记（分数及其 churn／bug-fix／行数拆解）\ ，
   让审查者看到历史上最容易坏的文件\ 。环境变量：
   ``PRTHINKER_RISK_WEIGHTED``\ 。

.. option:: --diff-entropy

   计算 diff 之 size + 目录分布 Shannon entropy\ ；分数越过 ``bomb``
   阈值时于评论顶端贴\ 「\ Consider splitting this PR\ 」\ 警示\ 。纯本机 CPU\ 、
   无 backend 调用\ 。环境变量：``PRTHINKER_DIFF_ENTROPY``\ 。

.. option:: --review-order

   加一个\ 「\ Suggested review order\ 」\ 注记\ ，用 repo knowledge graph
   的 import 边把变更文件按\ 「\ 被最多其他变更文件依赖\ 」\ 排前面\ ，最
   地基的文件标上\ 「\ start here\ 」\ ，让审查者先读基础变更再读其调用端\ 。
   Best-effort：KG store 不存在时略过\ 。环境变量：``PRTHINKER_REVIEW_ORDER``\ 。

.. option:: --change-map

   在评论内嵌一张小的 Mermaid 图\ ，画出\ *变更文件之间*\ 的 import 边
   （来自 repo knowledge graph）\ ，让改动的结构一眼可见\ 。GitHub 原生
   渲染 ```mermaid`` 区块\ 。变更文件之间没有 import 边时略过\ 。
   环境变量：``PRTHINKER_CHANGE_MAP``\ 。

.. option:: --auto-file-issues {none,off-diff,all}

   把审查 findings 自动开成 issue tracker 上的 issue\ 。\ ``off-diff``
   只开落在 diff hunks *之外*\ 的 findings —— 这些是平台会拒绝以
   inline comment 张贴\ 、原本只能留在 summary 文字里的发现\ 。
   ``all`` 则每个 finding 都开\ 。每张 issue 正文带指纹 marker
   （path + category + 规范化 comment 的哈希）\ ，重跑审查不会把同一个
   问题重复开单\ ；单次最多开 10 张新 issue\ 。支持 GitHub 与 GitLab\ ；
   best-effort —— API 失败绝不弄坏审查本体\ 。默认 ``none``\ 。
   环境变量：``PRTHINKER_AUTO_FILE_ISSUES``\ 。

.. option:: --issue-labels <labels>

   自动开的 issue 要套的标签\ ，逗号分隔（默认 ``prthinker``）\ 。
   环境变量：``PRTHINKER_ISSUE_LABELS``\ 。

review-file
-----------

对本地文件或 stdin 跑 pipeline。

.. code-block:: text

   prthinker review-file PATH
       [--backend {local,remote,openai,anthropic,gemini,cohere,mistral,claude-cli,codex-cli}]
       [--remote-url URL] [--remote-api-key TOKEN]
       [--model-name NAME] [--lora-path PATH]
       [--no-rag] [--remote-rag] [--rag-threshold 0.7]
       [--rules-dir PATH]
       [--per-file] [--inline-review] [--max-findings-per-file 10]
       [--counterfactual] [--provenance] [--judge] [--self-correct]
       [--diff-since-last] [--verify-suggestions]
       [--api-consistency] [--pr-classify] [--reproducibility-check]
       [--dep-upgrade-check] [--personas LIST]
       [--risk-weighted] [--diff-entropy]
       [--max-new-tokens 32768]
       [--steps a,b,c]
       [--output-dir PATH]

``PATH`` 可填 ``-`` 从 stdin 读 diff。

``--output-dir`` 会把每个 step 的原始输出增量写入磁盘──批量实验或调试
长跑时很有用。

``--steps`` 是逗号分隔的 step 名称列表；空（默认）就跑全部已注册的 step。

triage
------

对一份 diff 跑完所有\ *无需模型*\ 的 orientation 信号并打印非空区块。不加载
任何 backend,故瞬间完成且仅需 runner profile——可作为 push 前的本机检查,
或 GPU-free 的 CI gate,在完整 review 排程前先抓出冲突标记、Trojan-Source
字符、吞错、重命名、删除、mode 变更、大段粘贴、纯格式变更、覆盖缺口、
残留 debug 与延迟工作标记\ 。

.. code-block:: text

   prthinker triage
       [--diff-file PATH | --staged | --against REF]
       [--exit-nonzero-on-signal]

默认从 stdin 读 diff;\ ``--diff-file`` 从文件读,\ ``--staged`` 跑
``git diff --cached``\ ,\ ``--against REF`` 跑 ``git diff REF``\ （如
``origin/main``\ ）。加上 ``--exit-nonzero-on-signal`` 时,只要有任一信号
触发即 exit 1,可用以 gate CI 步骤;否则一律 exit 0(仅供参考)\ 。

.. code-block:: bash

   git diff origin/main | prthinker triage
   prthinker triage --staged --exit-nonzero-on-signal

此信号集即 PR 评论摘要下方所呈现者;各区块检测内容见
:doc:`../concepts/research-extensions`\ 。

aggregate
---------

把 ``review-pr --output-json`` 各 runner 写出的 partial review JSON
合一，post 出单一 summary + inline review + gate close。对应到
:doc:`../guide/github-actions` 描述的 matrix workflow。

.. code-block:: text

   prthinker aggregate
       --repo OWNER/NAME
       --pr-number N
       --github-token TOKEN
       --aggregate-from DIR
       [--marker '<!-- prthinker:summary -->']
       [--inline-review] [--judge]
       [--gate-on {none,warning,error}]
       [--platform {github,gitlab}]
       [--dry-run]

Aggregator 会递归扫 ``--aggregate-from`` 下所有 ``*.json``\ （所以
``actions/download-artifact`` 常见的「一个 matrix iteration 一个
目录」 layout 无须额外接线），反序列化每个 partial 为 ``ReviewResult``\ ，
按 path 对 ``per_file`` 去重（同路径 last-write-wins），跨 shard 合
``inline_findings`` + ``step_outputs`` + ``rag_docs``\ 。合完后再以
``/ask/submit`` 对 backend 取一段 3-5 句之 PR-wide overall summary，
塞进 ``step_outputs["total_summary"]``\ 并由 formatter 渲染为 PR 评论
顶部之 ``### Overall Summary``\ 。Post 路径与 ``review-pr`` 完全相同
──同样的 comment marker upsert、同样的 ``submit_inline_review`` event
mapping（\ ``--judge`` 开启时做 verdict aggregation）、同样的 gate
close。

若目录下没有 JSON（例如所有 matrix shard 因 backend 不通而 skip），
指令 log 一条 warning 并 exit 0；workflow 端 fallback 之 shell step
会用同一个 marker 贴一条「skipped」notice。

Env equivalents: ``PRTHINKER_AGGREGATE_FROM``\ （input dir）、
``PRTHINKER_COMMENT_MARKER``\ （marker）、``PRTHINKER_GATE_ON``\ （gate
floor）。其余由标准 ``GITHUB_REPOSITORY``\ 、\ ``PRTHINKER_PR_NUMBER``\ 、
``GITHUB_TOKEN`` 涵盖。

pr-summary
----------

从 PR 标题、描述、commit 信息与 diff 产生 Copilot 式 PR 摘要，并以专属
marker ``<!-- prthinker:pr-summary -->`` upsert 成一条独立评论（与
review summary 分开）。设计为在逐文件审查\ *之前*\ 执行──由
:doc:`../guide/github-actions` 之 ``enumerate`` job 调用──让 reviewer
在较慢的审查进行时即有概览。

.. code-block:: text

   prthinker pr-summary
       --repo OWNER/NAME            # 或 $GITHUB_REPOSITORY
       --pr-number N                # 或 $PRTHINKER_PR_NUMBER
       --github-token TOKEN         # 或 $GITHUB_TOKEN
       [--backend {local,remote,openai,anthropic,gemini,cohere,mistral,claude-cli,codex-cli}]
       [--remote-url URL] [--remote-api-key TOKEN]
       [--platform {github,gitlab,gitea}]
       [--dry-run]

它核对作者「所写」（标题、body、commit 主旨）与 diff「所做」是否一致，
并被要求点出任何落差。输出为 GitHub-flavoured Markdown，含
``### Overview``\ 、\ ``### Key changes``\ 、\ ``### Areas to review``
与 ``### Notes`` 等区段。

设计上为 best-effort：生成走注入之 backend，遇短暂故障（5xx、连接中
断、空回应）会重试数次；持续失败则 log warning 并 exit 0，使不稳定之
backend 永不阻挡 review matrix。``--dry-run`` 将渲染后之评论打印至
stdout 而不贴出。

Env equivalents：``PRTHINKER_BACKEND``\ / ``PRTHINKER_REMOTE_URL``\ /
``PRTHINKER_REMOTE_API_KEY`` 选择 backend；``GITHUB_REPOSITORY``\ 、
``PRTHINKER_PR_NUMBER``\ 、\ ``GITHUB_TOKEN`` 涵盖目标。

harvest-dismissed
-----------------

扫 PR／MR review comment，把 dismissed finding 追加到 JSONL store。

.. code-block:: text

   prthinker harvest-dismissed
       [--platform github|gitlab]
       [--platform-base-url URL]
       --repo OWNER/NAME
       --github-token TOKEN
       [--pr-number N | --max-prs 50]
       [--out .prthinker/dismissed.jsonl]

设 ``--pr-number`` 时只扫那一个 PR／MR；否则迭代最近 ``--max-prs`` 个依
更新时间排序的 closed PR／MR。GitHub 上，review comment 带 👎 reaction
或带驳回关键字的回复即视为 dismissed；GitLab 上则从 MR 的 diff
discussion 与 award emoji 读取同样的信号。``--repo``\ ／
``--github-token`` 默认读 ``GITHUB_REPOSITORY``\ ／``GITHUB_TOKEN``\ ，
并回退到 ``CI_PROJECT_PATH``\ ／``GITLAB_TOKEN``\ 。

harvest-accepted
----------------

扫 PR／MR 看是否有应用过的 suggestion 区块，追加到 JSONL store。

.. code-block:: text

   prthinker harvest-accepted
       [--platform github|gitlab]
       [--platform-base-url URL]
       --repo OWNER/NAME
       --github-token TOKEN
       [--pr-number N | --max-prs 50]
       [--out .prthinker/accepted.jsonl]

当 PR 的任一 commit message 以 ``Apply suggestion(s) from code review``
开头时即视为「有采纳过建议」（GitLab 另外比对其原生的
``Apply N suggestion(s) to M file(s)`` 消息）。每个带 ```suggestion```
区块的评论／diff note 都会保留。

adversarial-eval
----------------

把 prompt-injection 语料丢给当前 backend\ ，将每一笔调用之结果写入
SQLite\ 。本子命令\ **不输出**\ 任何汇总检测率 —— 聚合计算交给下游 SQL\ ，
原始输出保留以利审计\ 。

.. code-block:: text

   prthinker adversarial-eval
       --corpus PATH                # JSONL 语料（参考 seed.jsonl）
       --outcomes-path PATH         # SQLite 输出文件
       [--backend {local,remote,openai,anthropic,gemini,cohere,mistral,claude-cli,codex-cli}]
       [--remote-url URL] [--remote-api-key TOKEN]
       [--openai-model NAME] [--openai-api-key TOKEN]
       [--anthropic-model NAME] [--anthropic-api-key TOKEN]
       [--max-new-tokens 4096]

语料格式：每行一个 JSON 对象\ ，符合
:class:`prthinker.adversarial.AttackCase`\ 。随附之
``prthinker/adversarial_corpus/seed.jsonl`` 是手工撰写的种子\ ，
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

issue-fix
---------

针对一个 issue 定位相关文件\ 、提出经验证的 find/replace 编辑\ ，
并以 JSON 打印\ 。默认只读：除非给 ``--apply`` 或 ``--test-cmd``\ ，
否则绝不写入 work-tree\ 。

.. code-block:: text

   prthinker issue-fix "issue 文字"        # 或 '-' 读 stdin
       --workdir PATH                       # repository work-tree
       [--issue-file PATH]
       [--retriever {graph-rerank,graph,rerank,lexical}]
       [--top-k 10] [--max-retries 1]
       [--backend {local,remote,openai,anthropic,gemini,cohere,mistral,claude-cli,codex-cli}]
       [--output PATH] [--patch PATH]
       [--apply] [--test-cmd CMD] [--test-timeout 600]

每个提出的编辑都必须能逐字应用\ ，且应用后文件语法有效（Python）\ ；
无效的批次会附上失败原因重问一次\ 。\ ``--patch`` 写出 unified diff\ ，
``--apply`` 把编辑写入 work-tree\ ，\ ``--test-cmd`` 应用修复后执行该
命令作为 Pass@1 检查（失败时 exit 1）\ 。

issue-autofix
-------------

从 issue tracker（GitHub 或 GitLab）抓 issue\ ，用与 ``issue-fix``
相同的引擎提出经验证的修复\ ；加上 ``--open-pr`` 时会应用\ 、commit\ 、
push\ ，开一个正文带 ``Fixes #N`` 的 fix pull / merge request\ ，并把
链接评论回 issue\ 。不加 ``--open-pr`` 则是 dry run：只以 JSON 打印
提案与 patch\ ，不改动任何东西\ 。

.. code-block:: text

   prthinker issue-autofix
       --repo OWNER/NAME                    # GitLab：project 路径或 id
       --workdir PATH                       # scratch clone（--open-pr 时会被改动）
       (--issue-number N | --issue-label LABEL [--limit 3])
       [--platform {github,gitlab}] [--gitlab-url URL]
       [--github-token TOKEN]               # 或 $GITHUB_TOKEN / $GITLAB_TOKEN
       [--retriever {graph-rerank,graph,rerank,lexical}]
       [--top-k 10] [--max-retries 1]
       [--open-pr] [--no-draft]
       [--base-branch NAME] [--branch-prefix issue-fix]
       [--test-cmd CMD] [--test-timeout 600]
       [--output PATH]

重点行为：

* ``--test-cmd`` 是一道闸门：命令对应用后的修复执行失败时\ ，不会
  push 分支\ 、不会开 PR —— 结果记录 ``test command failed``\ 。
* fix PR / MR 默认是 **draft**\ （``--no-draft`` 直接开成待审）\ ；
  合并后 ``Fixes #N`` 自动关闭 issue\ 。
* ``--issue-label`` 批次模式在 issue 之间还原起始 git ref\ ，一个修复
  不会渗入下一个\ ；单个 issue 失败会记录错误结果\ ，批次继续\ 。
* ``--workdir`` 请指向一个专用的 scratch clone\ ，其 ``origin``
  remote 必须是 token 能 push 的 —— 循环会在里面执行
  ``git checkout -B``\ 、\ ``commit``\ 、\ ``push --force-with-lease``\ 。
* 只有所有尝试的 issue 都产出有效修复时\ ，exit code 才是 ``0``\ 。

Exit code
---------

* ``0``\ ──成功（含 dry-run 与零 finding 的情况）。
* ``1``\ ──runtime 失败（network、GPU、parse error）。\ ``--gate-on`` 启用时，
  Check Run 在传递错误前会被 PATCH 为 ``failure``\ 。
* ``2``\ ──argparse 参数解析或校验错误。
