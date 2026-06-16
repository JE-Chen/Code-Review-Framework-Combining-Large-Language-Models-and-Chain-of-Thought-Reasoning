# Code Review Framework - Architecture Diagram

## System Overview

```mermaid
%%{init: {'themeVariables': {'fontSize': '52px', 'fontFamily': 'Arial, "Microsoft JhengHei", sans-serif'}, 'flowchart': {'padding': 36, 'nodeSpacing': 100, 'rankSpacing': 120}}}%%
graph TB
    subgraph INPUT["① 輸入層 Input"]
        CODE["Source Code<br/>ChatGPT / Copilot<br/>(bad_data · code_diff · only_code)"]
    end

    subgraph RAG["② 檢索層 RAG"]
        RAG_DATA["Rule Documents"]
        EMB["EmbeddingGemma-300m (default, threshold 0.32)<br/>Qwen3-Embedding-4B (legacy, threshold 0.7)"]
        FAISS["FAISS Index<br/>(calibrated threshold per model)"]
        RAG_DATA --> EMB --> FAISS
    end

    subgraph PIPE["③ 推論層 Pipelines + Model"]
        COT["CoT Pipeline"]
        SKILLS["Skills Pipeline"]
        SINGLE["Single Prompt"]
        QWEN["Qwen3-Coder-30B-A3B<br/>+ LoRA · 4-bit Quantization"]
        COT --> QWEN
        SKILLS --> QWEN
        SINGLE --> QWEN
    end

    subgraph EVAL["④ 評估層 Evaluation"]
        JUDGE["LLM-as-Judge<br/>5 Dimensions"]
        CRSCORE["CRScore"]
        HUMAN["Human Judge"]
    end

    CODE --> EMB
    CODE --> COT
    CODE --> SKILLS
    CODE --> SINGLE
    FAISS -->|Retrieved Rules| COT
    FAISS -->|Retrieved Rules| SKILLS

    QWEN --> JUDGE
    QWEN --> CRSCORE
    QWEN --> HUMAN

    style INPUT fill:#e1f5fe,stroke:#01579b,stroke-width:6px,color:#1a1a1a
    style RAG fill:#f3e5f5,stroke:#4a148c,stroke-width:6px,color:#1a1a1a
    style PIPE fill:#fff3e0,stroke:#e65100,stroke-width:6px,color:#1a1a1a
    style EVAL fill:#efebe9,stroke:#3e2723,stroke-width:6px,color:#1a1a1a

    style CODE fill:#ffffff,stroke:#01579b,stroke-width:5px,color:#1a1a1a
    style RAG_DATA fill:#ffffff,stroke:#4a148c,stroke-width:5px,color:#1a1a1a
    style EMB fill:#ffffff,stroke:#4a148c,stroke-width:5px,color:#1a1a1a
    style FAISS fill:#ffffff,stroke:#4a148c,stroke-width:5px,color:#1a1a1a
    style COT fill:#e8f5e9,stroke:#1b5e20,stroke-width:5px,color:#1a1a1a
    style SKILLS fill:#fce4ec,stroke:#b71c1c,stroke-width:5px,color:#1a1a1a
    style SINGLE fill:#fff9c4,stroke:#f57f17,stroke-width:5px,color:#1a1a1a
    style QWEN fill:#ffffff,stroke:#e65100,stroke-width:5px,color:#1a1a1a
    style JUDGE fill:#ffffff,stroke:#3e2723,stroke-width:5px,color:#1a1a1a
    style CRSCORE fill:#ffffff,stroke:#3e2723,stroke-width:5px,color:#1a1a1a
    style HUMAN fill:#ffffff,stroke:#3e2723,stroke-width:5px,color:#1a1a1a
    linkStyle default stroke:#37474f,stroke-width:4px
```

## CoT Code Review Detailed Flow

```mermaid
%%{init: {'themeVariables': {'fontSize': '52px', 'fontFamily': 'Arial, "Microsoft JhengHei", sans-serif'}, 'flowchart': {'padding': 36, 'nodeSpacing': 100, 'rankSpacing': 100}}}%%
graph TB
    CODE[/"Source Code"/]
    CODE --> EMB["Query Embedding"]
    EMB --> FAISS["FAISS Search"]
    FAISS --> RULES[/"Retrieved Rules"/]
    RULES --> INJECT["Inject RAG Rules into Global Template"]

    INJECT --> S1 & S2 & S3 & S4

    subgraph COT["Chain-of-Thought Steps (parallel)"]
        S1["Step 1: Summary<br/>變更摘要 · 影響範圍 · 風險評估"]
        S2["Step 2: Code Review<br/>可讀性 · 命名規範 · 邏輯錯誤"]
        S3["Step 3: Linter<br/>rule_id · severity · line · suggestion"]
        S4["Step 4: Code Smell<br/>Type · Location · Priority · Refactoring"]
    end

    S1 & S2 & S3 & S4 --> TS

    TS["Step 5: Total Summary<br/>綜合所有結果 · Merge 建議 · Follow-up<br/>（Linter + Code Smell 結果亦直接輸入 Judge）"]

    TS --> JUDGE["LLM Judge<br/>Readability · Constructiveness · Correctness<br/>Coverage & Extractability · Comprehensiveness<br/>每項 1-100 分"]

    JUDGE --> FINAL[/"Final Score & Recommendation"/]

    style CODE fill:#e1f5fe,stroke:#01579b,stroke-width:6px,color:#1a1a1a
    style EMB fill:#f3e5f5,stroke:#4a148c,stroke-width:6px,color:#1a1a1a
    style FAISS fill:#f3e5f5,stroke:#4a148c,stroke-width:6px,color:#1a1a1a
    style RULES fill:#f3e5f5,stroke:#4a148c,stroke-width:6px,color:#1a1a1a
    style INJECT fill:#f1f8e9,stroke:#33691e,stroke-width:6px,color:#1a1a1a
    style S1 fill:#e8f5e9,stroke:#1b5e20,stroke-width:6px,color:#1a1a1a
    style S2 fill:#e8f5e9,stroke:#1b5e20,stroke-width:6px,color:#1a1a1a
    style S3 fill:#e8f5e9,stroke:#1b5e20,stroke-width:6px,color:#1a1a1a
    style S4 fill:#e8f5e9,stroke:#1b5e20,stroke-width:6px,color:#1a1a1a
    style COT fill:#e8f5e9,stroke:#1b5e20,stroke-width:6px,color:#1a1a1a
    style TS fill:#fff3e0,stroke:#e65100,stroke-width:6px,color:#1a1a1a
    style JUDGE fill:#efebe9,stroke:#3e2723,stroke-width:6px,color:#1a1a1a
    style FINAL fill:#fff9c4,stroke:#f57f17,stroke-width:6px,color:#1a1a1a
    linkStyle default stroke:#37474f,stroke-width:4px
```

## Knowledge Distillation Training Flow

```mermaid
%%{init: {'themeVariables': {'fontSize': '52px', 'fontFamily': 'Arial, "Microsoft JhengHei", sans-serif'}, 'flowchart': {'padding': 36, 'nodeSpacing': 100, 'rankSpacing': 100}}}%%
graph TB
    TEACHER["Teacher LLM<br/>大型高能力模型"]
    GEN_PROMPT["generate_datas_prompt.md<br/>蒸餾用提示模板"]
    TEACHER --> GEN
    GEN_PROMPT --> GEN

    GEN["Synthetic Data Generation<br/>由 Teacher 產生帶 CoT 的審查樣本"]
    GEN --> JSONL[/"qwen3_train_data.jsonl<br/>{Instruction, question, think, answer}"/]

    JSONL --> TOK["Tokenize<br/>build_prompt + concat answer"]
    TOK --> MASK["Label Masking<br/>prompt 標 -100，僅 answer 計算 loss"]

    BASE["Student Base Model<br/>Qwen3-Coder-30B-A3B-Instruct"]
    BNB["BitsAndBytesConfig<br/>NF4 4-bit + bf16 compute"]
    BASE --> QLORA
    BNB --> QLORA
    QLORA["QLoRA Quantized Load<br/>prepare_model_for_kbit_training"]

    LORA_CFG["LoRA Adapter<br/>r=64, α=64, dropout=0.1<br/>q/k/v/o + gate/up/down_proj"]
    QLORA --> INJECT
    LORA_CFG --> INJECT
    INJECT["get_peft_model<br/>注入 LoRA 可訓練參數"]

    MASK --> TRAIN
    INJECT --> TRAIN
    TRAIN["Trainer (HF Transformers)<br/>cosine LR · warmup 0.1<br/>grad accum 64 · adamw_8bit<br/>gradient_checkpointing"]

    TRAIN --> ADAPTER[/"LoRA Adapter Weights<br/>outputs-lora-qwen3-coder-30b/"/]
    ADAPTER -.optional.-> MERGE["merge_and_unload<br/>合併回 Base 權重"]
    ADAPTER --> SERVE["Inference Pipeline<br/>CoT / Skills / Single Prompt"]

    style TEACHER fill:#f3e5f5,stroke:#4a148c,stroke-width:6px,color:#1a1a1a
    style GEN_PROMPT fill:#f3e5f5,stroke:#4a148c,stroke-width:6px,color:#1a1a1a
    style GEN fill:#f3e5f5,stroke:#4a148c,stroke-width:6px,color:#1a1a1a
    style JSONL fill:#e1f5fe,stroke:#01579b,stroke-width:6px,color:#1a1a1a
    style TOK fill:#e1f5fe,stroke:#01579b,stroke-width:6px,color:#1a1a1a
    style MASK fill:#e1f5fe,stroke:#01579b,stroke-width:6px,color:#1a1a1a
    style BASE fill:#fff3e0,stroke:#e65100,stroke-width:6px,color:#1a1a1a
    style BNB fill:#fff3e0,stroke:#e65100,stroke-width:6px,color:#1a1a1a
    style QLORA fill:#fff3e0,stroke:#e65100,stroke-width:6px,color:#1a1a1a
    style LORA_CFG fill:#fff3e0,stroke:#e65100,stroke-width:6px,color:#1a1a1a
    style INJECT fill:#fff3e0,stroke:#e65100,stroke-width:6px,color:#1a1a1a
    style TRAIN fill:#e8f5e9,stroke:#1b5e20,stroke-width:6px,color:#1a1a1a
    style ADAPTER fill:#fff9c4,stroke:#f57f17,stroke-width:6px,color:#1a1a1a
    style MERGE fill:#efebe9,stroke:#3e2723,stroke-width:6px,color:#1a1a1a
    style SERVE fill:#efebe9,stroke:#3e2723,stroke-width:6px,color:#1a1a1a
    linkStyle default stroke:#37474f,stroke-width:4px
```

## PRThinker Runtime Architecture

```mermaid
%%{init: {'themeVariables': {'fontSize': '52px', 'fontFamily': 'Arial, "Microsoft JhengHei", sans-serif'}, 'flowchart': {'padding': 36, 'nodeSpacing': 100, 'rankSpacing': 110}}}%%
graph TB
    subgraph CLI["① CLI surface"]
        REVIEW["review-pr / review-file"]
        HARV["harvest-dismissed<br/>harvest-accepted"]
        ADV["adversarial-eval"]
        HOOK["hook / mcp / stats / report"]
    end

    subgraph PIPE["② CoTPipeline (orchestrator)"]
        STEPS["5 CoT steps<br/>+ optional<br/>InlineFindings · Judge"]
        EXT["Research-grade extensions (opt-in)<br/>13 mechanisms"]
    end

    subgraph BACKENDS["③ Pluggable backends (Strategy)"]
        BLOCAL["LocalHFBackend<br/>Qwen3-Coder-30B + LoRA<br/>(NF4 4-bit)"]
        BREMOTE["RemoteHttpBackend<br/>FastAPI /ask · /review"]
        BOAI["OpenAICompatBackend<br/>OpenAI · Azure · vLLM · Ollama"]
        BANT["AnthropicBackend<br/>Claude Messages API"]
    end

    subgraph PLAT["④ PlatformAdapter (Strategy)"]
        GH["GitHubAdapter<br/>diff · comments · gate"]
        GL["GitLabAdapter<br/>raw_diffs · notes · status"]
    end

    subgraph CORPORA["⑤ Learned corpora (Repository)"]
        DISMISSED["dismissed.jsonl"]
        ACCEPTED["accepted.jsonl"]
        RAG["FAISS RAG index"]
        DIFFCACHE["diff-cache.sqlite"]
    end

    REVIEW --> PIPE
    ADV --> BACKENDS
    PIPE --> BACKENDS
    PIPE --> EXT
    PIPE --> PLAT
    PIPE --> CORPORA

    style CLI fill:#e1f5fe,stroke:#01579b,stroke-width:6px,color:#1a1a1a
    style PIPE fill:#fff3e0,stroke:#e65100,stroke-width:6px,color:#1a1a1a
    style BACKENDS fill:#f3e5f5,stroke:#4a148c,stroke-width:6px,color:#1a1a1a
    style PLAT fill:#fce4ec,stroke:#b71c1c,stroke-width:6px,color:#1a1a1a
    style CORPORA fill:#efebe9,stroke:#3e2723,stroke-width:6px,color:#1a1a1a
    style EXT fill:#e8f5e9,stroke:#1b5e20,stroke-width:5px,color:#1a1a1a

    style REVIEW fill:#ffffff,stroke:#01579b,stroke-width:5px,color:#1a1a1a
    style HARV fill:#ffffff,stroke:#01579b,stroke-width:5px,color:#1a1a1a
    style ADV fill:#ffffff,stroke:#01579b,stroke-width:5px,color:#1a1a1a
    style HOOK fill:#ffffff,stroke:#01579b,stroke-width:5px,color:#1a1a1a
    style STEPS fill:#ffffff,stroke:#e65100,stroke-width:5px,color:#1a1a1a
    style BLOCAL fill:#ffffff,stroke:#4a148c,stroke-width:5px,color:#1a1a1a
    style BREMOTE fill:#ffffff,stroke:#4a148c,stroke-width:5px,color:#1a1a1a
    style BOAI fill:#ffffff,stroke:#4a148c,stroke-width:5px,color:#1a1a1a
    style BANT fill:#ffffff,stroke:#4a148c,stroke-width:5px,color:#1a1a1a
    style GH fill:#ffffff,stroke:#b71c1c,stroke-width:5px,color:#1a1a1a
    style GL fill:#ffffff,stroke:#b71c1c,stroke-width:5px,color:#1a1a1a
    style DISMISSED fill:#ffffff,stroke:#3e2723,stroke-width:5px,color:#1a1a1a
    style ACCEPTED fill:#ffffff,stroke:#3e2723,stroke-width:5px,color:#1a1a1a
    style RAG fill:#ffffff,stroke:#3e2723,stroke-width:5px,color:#1a1a1a
    style DIFFCACHE fill:#ffffff,stroke:#3e2723,stroke-width:5px,color:#1a1a1a
    linkStyle default stroke:#37474f,stroke-width:4px
```

## Project Directory Structure

```
Code-Review-Framework/
├── prthinker/                        # Standalone Python package
│   ├── __init__.py
│   ├── __main__.py                   # python -m prthinker
│   ├── cli.py                        # entry point: handler registry + main()
│   ├── cli_parser.py                 # argparse construction (shared + per-cmd)
│   ├── cli_review.py                 # review-file / review-pr handlers
│   ├── cli_commands.py               # corpora / KG / maintenance handlers
│   ├── config.py                     # dataclass-based runtime config
│   ├── pipeline.py                   # CoTPipeline orchestrator
│   ├── steps.py                      # ReviewStep ABC + 5 registered steps
│   ├── schemas.py                    # Pydantic v2 wire-format models
│   ├── findings.py                   # JSON-array parser + sanitizer
│   ├── formatters.py                 # Markdown PR-comment renderer
│   ├── rag.py                        # RAGRetriever abstractions
│   ├── rules.py                      # per-repo rule loader
│   ├── repo_config.py                # .prthinker.yaml parser
│   ├── checks.py                     # GitHub Check Run gate
│   ├── ci_signals.py                 # Failed-job log integration
│   ├── github_api.py                 # raw GH REST helpers
│   ├── platforms/                    # PlatformAdapter (Strategy)
│   │   ├── base.py
│   │   ├── github.py
│   │   └── gitlab.py
│   ├── backends/                     # InferenceBackend (Strategy)
│   │   ├── base.py
│   │   ├── local.py                  # LocalHFBackend (Qwen + LoRA)
│   │   ├── remote.py                 # RemoteHttpBackend
│   │   ├── openai_compat.py
│   │   ├── anthropic.py
│   │   └── wrappers.py               # cache + telemetry wrappers
│   ├── accepted.py                   # AcceptedExamplesStore + Retriever
│   ├── dismissed.py                  # DismissedFilter
│   ├── harvest.py                    # harvest-dismissed / harvest-accepted
│   ├── cache.py                      # SQLite prompt cache
│   ├── telemetry.py                  # per-call token / latency / cost
│   ├── pricing.py                    # backend → $/Mtok table
│   ├── report.py                     # cross-store longitudinal report
│   ├── redaction.py                  # secret-pattern scrubber
│   ├── mcp_server.py                 # MCP stdio integration
│   ├── auto_fix.py                   # apply suggestions + open fix PR
│   ├── self_review.py                # second-pass noise filter
│   ├── judge.py                      # per-file verdict aggregation
│   ├── dialogue.py                   # --reply-to-author harvesting
│   ├── counterfactual.py             # mutation-style review parser
│   ├── adversarial.py                # prompt-injection bypass detection
│   ├── adversarial_eval.py           # adversarial-eval subcommand
│   ├── adversarial_corpus/           # Seed JSONL + README
│   ├── review_cache.py               # Force-push differential cache
│   ├── sandbox.py                    # --verify-suggestions sandbox
│   ├── api_consistency.py            # Cross-language drift step
│   ├── pr_classifier.py              # PR-type adaptive review
│   ├── reproducibility.py            # Reviewer disagreement signal
│   ├── dep_upgrade.py                # Dependency-upgrade impact
│   ├── personas.py                   # Reviewer-personas + conflict
│   ├── risk_score.py                 # Per-file risk scorer
│   └── diff_entropy.py               # Diff-bomb detector
├── tests/                            # ~274 pytest cases
├── codes/                            # Research / training scripts (legacy)
│   ├── run/                          #   cot.py / skills.py / fastapi_server.py
│   ├── train/                        #   LoRA fine-tuning entry points
│   └── util/                         #   hf_model_util.py + faiss_util.py + server_metrics.py
├── datas/                            # RAG rules + experiment fixtures
├── docs/                             # Sphinx (en + zh-TW + zh-CN, single tree)
├── docker/                           # Self-host: Dockerfile + compose (port 9000)
├── paper/                            # Manuscript + pptxgenjs slide build
├── .github/workflows/prthinker.yml   # GHA: review-pr with graceful skip
├── .prospector.yaml                  # D213 disabled, D212 selected
├── pyproject.toml                    # [tool.bandit] + [tool.pydocstyle]
└── READMEs/
    ├── CLAUDE.md                     # Project guidelines (this file's neighbour)
    ├── README.zh-TW.md / README.zh-CN.md
    ├── setup.{md,zh-TW.md,zh-CN.md}
    ├── features.{md,zh-TW.md,zh-CN.md}
    ├── architecture.md               # This file
    └── Human_Judge.md                # Human evaluation guide
```
