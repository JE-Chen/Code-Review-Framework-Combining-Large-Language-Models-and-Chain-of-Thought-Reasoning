快速开始
========

三个最简的场景──挑符合你环境的那个。

对本地 diff 跑审查（远程 backend）
----------------------------------

最便宜的试用方式：把 reviewer 指向已部署的推理服务器，喂它一份 diff 文件。

.. code-block:: bash

   git diff main..HEAD > my-change.diff

   reviewmind review-file my-change.diff \
       --backend remote \
       --remote-url https://my-host:8000 \
       --per-file --inline-review

stdout 会打印整合好的 markdown 评论与 inline findings 的数量。不需要 PR、
也不需要 GitHub token。

完整审查 PR
-----------

这就是 GitHub Action 底层实际在跑的东西：

.. code-block:: bash

   export GITHUB_TOKEN=ghp_...
   export REVIEWMIND_REMOTE_URL=https://my-host:8000

   reviewmind review-pr \
       --repo owner/name \
       --pr-number 42 \
       --gate-on error \
       --include-ci-signals

按顺序它会：

1. 通过 GitHub REST 拿 PR diff 与 head SHA。
2. （可选）\ ``--include-ci-signals`` 抓失败 job 的末端日志，前置成
   ``# CI Failure Signals`` 区块。
3. 对 head SHA 开一个 ``in_progress`` 的 Check Run。
4. 把 diff 切成逐文件 chunk，每个文件对远程服务器叫一次 ``/review``\ 。
5. 聚合 findings，在服务器端套用 dismissed 相似度过滤。
6. 对 PR upsert 一条可折叠的总结评论。
7. 提交一笔 inline review，每个 finding 都附 ``suggestion`` 区块。
8. 根据 ``--gate-on`` 结算 Check Run 为 ``success`` 或 ``failure``\ 。

本地 in-process pipeline（GPU 机器）
------------------------------------

开发或批量实验时用──不接服务器、不碰 GitHub：

.. code-block:: bash

   # 跑遍 datas/code_to_detect/bad_data/Python/Copilot 下每一个文件
   python -m codes.run.cot

   # 或对单个文件做一次审查
   reviewmind review-file path/to/code.py \
       --backend local \
       --model-name Qwen/Qwen3-Coder-30B-A3B-Instruct \
       --lora-path ../train/outputs-lora-qwen3-coder-30b

把学习语料 bootstrap 起来
-------------------------

当你已经积累了一些 PR 历史，可以把它们收进 JSONL store：

.. code-block:: bash

   # 作者按 👎 或回「false positive」的评论
   reviewmind harvest-dismissed \
       --repo owner/name --max-prs 100 \
       --out .reviewmind/dismissed.jsonl

   # 含「Apply suggestion」commit 的 PR
   reviewmind harvest-accepted \
       --repo owner/name --max-prs 100 \
       --out .reviewmind/accepted.jsonl

然后让服务器指向它们：

.. code-block:: bash

   export REVIEWMIND_DISMISSED_PATH=.reviewmind/dismissed.jsonl
   export REVIEWMIND_ACCEPTED_PATH=.reviewmind/accepted.jsonl
   uvicorn codes.run.fastapi_server:app --host 0.0.0.0 --port 8000

语义细节请见 :doc:`../concepts/corpora`。
