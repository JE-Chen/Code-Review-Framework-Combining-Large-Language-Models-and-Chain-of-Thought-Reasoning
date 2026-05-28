Quickstart
==========

Three minimal scenarios — pick whichever matches your setup.

Review a local diff (remote backend)
------------------------------------

The cheapest way to try the reviewer: point it at a hosted inference
server and feed it a diff file.

.. code-block:: bash

   git diff main..HEAD > my-change.diff

   reviewmind review-file my-change.diff \
       --backend remote \
       --remote-url https://my-host:8000 \
       --per-file --inline-review

This prints the consolidated markdown comment and a count of inline
findings to stdout. No PR or GitHub token needed.

Review a PR end-to-end
----------------------

This is what the GitHub Action runs under the hood:

.. code-block:: bash

   export GITHUB_TOKEN=ghp_...
   export REVIEWMIND_REMOTE_URL=https://my-host:8000

   reviewmind review-pr \
       --repo owner/name \
       --pr-number 42 \
       --gate-on error \
       --include-ci-signals

What it does, in order:

1. Fetches the PR diff and head SHA via GitHub REST.
2. Optionally fetches failed-job tail logs (``--include-ci-signals``) and
   prepends them as a ``# CI Failure Signals`` block.
3. Opens an ``in_progress`` Check Run on the head SHA.
4. Parses the diff into per-file chunks; calls ``/review`` per file on the
   remote server.
5. Aggregates findings, applies dismissed-similarity filter on the server
   side.
6. Upserts a collapsible summary comment on the PR.
7. Submits one inline review with each finding as a ``suggestion`` block.
8. Completes the Check Run with ``success`` or ``failure`` based on
   ``--gate-on``.

Local in-process pipeline (GPU box)
-----------------------------------

For development or batch experiments — no server, no GitHub:

.. code-block:: bash

   # Review every file under datas/code_to_detect/bad_data/Python/Copilot
   python -m codes.run.cot

   # Or one-off review of a single file
   reviewmind review-file path/to/code.py \
       --backend local \
       --model-name Qwen/Qwen3-Coder-30B-A3B-Instruct \
       --lora-path ../train/outputs-lora-qwen3-coder-30b

Bootstrap the learned corpora
-----------------------------

Once you have history of past PRs, harvest them into JSONL stores:

.. code-block:: bash

   # Comments authors thumbed-down or replied "false positive" to
   reviewmind harvest-dismissed \
       --repo owner/name --max-prs 100 \
       --out .reviewmind/dismissed.jsonl

   # PRs that contain "Apply suggestion" commits
   reviewmind harvest-accepted \
       --repo owner/name --max-prs 100 \
       --out .reviewmind/accepted.jsonl

Then point the server at them:

.. code-block:: bash

   export REVIEWMIND_DISMISSED_PATH=.reviewmind/dismissed.jsonl
   export REVIEWMIND_ACCEPTED_PATH=.reviewmind/accepted.jsonl
   uvicorn codes.run.fastapi_server:app --host 0.0.0.0 --port 8000

See :doc:`/concepts/corpora` for the semantics.
