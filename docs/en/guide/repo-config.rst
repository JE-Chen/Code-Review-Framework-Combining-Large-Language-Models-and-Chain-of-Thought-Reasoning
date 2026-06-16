Repo-level configuration
========================

Drop a ``.prthinker.yaml`` at the repo root to centralize every
prthinker setting that isn't a secret. The CLI loads it on every
invocation and uses it as the default layer beneath environment
variables and command-line flags.

Resolution order (highest priority last)
----------------------------------------

1. Package built-in defaults.
2. ``.prthinker.yaml`` in the current directory (or ``--config PATH``).
3. Environment variables (``PRTHINKER_*``, ``OPENAI_API_KEY``, …).
4. Command-line flags.

**Secrets never live in the YAML.** API keys, tokens, and the GitHub
token are read exclusively from environment variables so a committed
config file cannot leak credentials.

Schema
------

.. code-block:: yaml

   # .prthinker.yaml — example with everything turned on
   backend: openai                # local | remote | openai | anthropic
   max_new_tokens: 8192

   per_file: true
   inline_review: true
   max_findings_per_file: 10

   rag:
     enabled: true
     threshold: 0.7
     rules_dir: ./team-rules      # optional; *.md files become team rules
     remote: false                # call /rag instead of loading FAISS locally

   gate:
     severity: error              # none | warning | error
                                  # NB: 'severity' not 'on' — YAML 1.1 parses
                                  # `on` as boolean True.

   ci_signals:
     enabled: true
     max_jobs: 5
     tail_chars: 4000

   cache:
     enabled: true
     path: .prthinker/cache.sqlite
     ttl_days: 7                  # set null to disable TTL

   telemetry:
     enabled: true
     path: .prthinker/telemetry.sqlite

   stores:
     dismissed: .prthinker/dismissed.jsonl
     accepted: .prthinker/accepted.jsonl

   local:
     model: Qwen/Qwen3-Coder-30B-A3B-Instruct
     lora_path: ../train/outputs-lora-qwen3-coder-30b

   openai:
     model: gpt-4o-mini
     base_url: https://api.openai.com/v1
     # api_key: comes from $OPENAI_API_KEY or $PRTHINKER_OPENAI_API_KEY
     # organization: optional

   anthropic:
     model: claude-opus-4-7
     base_url: https://api.anthropic.com
     version: "2023-06-01"
     # api_key: comes from $ANTHROPIC_API_KEY or $PRTHINKER_ANTHROPIC_API_KEY

   remote:
     url: https://my-inference-host:9000
     timeout_seconds: 600
     use_pipeline_endpoint: true   # call /review instead of /ask-per-step

What it does not cover
----------------------

* **Secrets** — by design.
* ``GITHUB_TOKEN`` / ``GITHUB_REPOSITORY`` — supplied by Actions or the
  shell.
* ``--pr-number`` / ``--dry-run`` / ``--steps`` — per-invocation, not
  per-repo.

Validation
----------

The loader is a Pydantic v2 model with ``extra="forbid"``: unknown keys
raise a clear validation error rather than silently being ignored. Run
``prthinker review-file - --config .prthinker.yaml`` with no stdin to
get a fast schema check.

Tips
----

* Commit ``.prthinker.yaml`` so reviewers see config changes in PRs
  alongside the code change that needed them.
* Keep ``.prthinker/cache.sqlite`` and ``.prthinker/telemetry.sqlite``
  in ``.gitignore`` — they're machine-generated state, not config.
* The same YAML works for both the runner (in your GHA workflow) and the
  server. Point both at the same file when one host hosts both.
