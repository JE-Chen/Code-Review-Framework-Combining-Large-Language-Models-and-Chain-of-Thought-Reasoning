快速開始
========

三個最簡的情境──挑符合你環境的那個。

對本機 diff 跑審查（遠端 backend）
----------------------------------

最便宜的試用方式：把 reviewer 指向已部署的推論伺服器，餵它一份 diff 檔。

.. code-block:: bash

   git diff main..HEAD > my-change.diff

   reviewmind review-file my-change.diff \
       --backend remote \
       --remote-url https://my-host:8000 \
       --per-file --inline-review

stdout 會印出整合好的 markdown 留言與 inline findings 的數量。不需要 PR、
也不需要 GitHub token。

完整審查 PR
-----------

這就是 GitHub Action 底下實際在跑的東西：

.. code-block:: bash

   export GITHUB_TOKEN=ghp_...
   export REVIEWMIND_REMOTE_URL=https://my-host:8000

   reviewmind review-pr \
       --repo owner/name \
       --pr-number 42 \
       --gate-on error \
       --include-ci-signals

按順序它會：

1. 透過 GitHub REST 拿 PR diff 與 head SHA。
2. （可選）\ ``--include-ci-signals`` 抓失敗 job 的尾端 log，前置成
   ``# CI Failure Signals`` 區塊。
3. 對 head SHA 開一個 ``in_progress`` 的 Check Run。
4. 把 diff 切成逐檔 chunk，每個檔案對遠端伺服器叫一次 ``/review``\ 。
5. 聚合 findings，在伺服器端套用 dismissed 相似度過濾。
6. 對 PR upsert 一條可摺疊的總結留言。
7. 提交一筆 inline review，每個 finding 都附 ``suggestion`` 區塊。
8. 根據 ``--gate-on`` 結算 Check Run 為 ``success`` 或 ``failure``\ 。

本機 in-process pipeline（GPU 機器）
------------------------------------

開發或批次實驗時用──不接伺服器、不碰 GitHub：

.. code-block:: bash

   # 跑遍 datas/code_to_detect/bad_data/Python/Copilot 下每一個檔
   python -m codes.run.cot

   # 或對單一檔案做一次審查
   reviewmind review-file path/to/code.py \
       --backend local \
       --model-name Qwen/Qwen3-Coder-30B-A3B-Instruct \
       --lora-path ../train/outputs-lora-qwen3-coder-30b

把學習語料 bootstrap 起來
-------------------------

當你已經累積了一些 PR 歷史，可以把它們收進 JSONL store：

.. code-block:: bash

   # 作者按 👎 或回「false positive」的留言
   reviewmind harvest-dismissed \
       --repo owner/name --max-prs 100 \
       --out .reviewmind/dismissed.jsonl

   # 含有「Apply suggestion」commit 的 PR
   reviewmind harvest-accepted \
       --repo owner/name --max-prs 100 \
       --out .reviewmind/accepted.jsonl

然後讓伺服器指向它們：

.. code-block:: bash

   export REVIEWMIND_DISMISSED_PATH=.reviewmind/dismissed.jsonl
   export REVIEWMIND_ACCEPTED_PATH=.reviewmind/accepted.jsonl
   uvicorn codes.run.fastapi_server:app --host 0.0.0.0 --port 8000

語義細節請見 :doc:`/concepts/corpora`。
