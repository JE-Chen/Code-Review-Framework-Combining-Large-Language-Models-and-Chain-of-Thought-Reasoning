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
        EMB["Qwen3-Embedding-4B"]
        FAISS["FAISS Index<br/>(threshold ≥ 0.7)"]
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

## Project Directory Structure

```
Code-Review-Framework/
├── codes/
│   ├── run/                          # Main Execution
│   │   ├── cot.py                    # CoT Pipeline Entry Point
│   │   ├── skills.py                 # Skills Pipeline Entry Point
│   │   ├── single_prompt.py          # Single Prompt Baseline
│   │   ├── run_single_prompt.py      # Single Prompt Runner
│   │   ├── fastapi_server.py         # FastAPI /ask Endpoint
│   │   ├── ask_functions.py          # RAG Query Helper
│   │   ├── build_our_llm_judge.py    # Build Judge Prompts
│   │   ├── build_our_llm_judge_single_prompt.py
│   │   ├── build_crscore_llm_judge.py
│   │   ├── CoT_Prompts/             # CoT Prompt Templates
│   │   │   ├── global_rule.py        #   Global Review Rules + RAG Injection
│   │   │   ├── first_summary_prompt.py  # PR Summary
│   │   │   ├── first_code_review.py  #   Initial Review
│   │   │   ├── linter.py            #   Linter Analysis
│   │   │   ├── code_smell_detector.py # Code Smell Detection
│   │   │   ├── step_by_step_analysis.py # Step-by-Step Analysis
│   │   │   ├── total_summary.py      #   Final Synthesis
│   │   │   ├── judge.py             #   LLM Judge Template (5 dims)
│   │   │   └── CRSCORE/             #   CRScore Evaluation
│   │   └── Skills/                  # Skills Prompt Templates
│   │       ├── code_review.py        #   Direct Review
│   │       └── code_explainer.py     #   Code Explanation
│   ├── train/                        # Model Training (LoRA)
│   │   ├── qwen3-coder-30b.py
│   │   ├── qwen3-30b.py
│   │   ├── qwen2.5-7b.py
│   │   └── qwen3.1-7b.py
│   ├── util/                         # Utilities
│   │   ├── qwen3_util.py            #   Model Loading + Inference
│   │   ├── faiss_util.py            #   FAISS RAG Engine
│   │   ├── memory.py                #   Memory Utils
│   │   └── prompt_define.py
│   └── base_model_*/                # Baseline Experiments
│       ├── with_vector_database/     #   With RAG
│       └── without_vector_database/  #   Without RAG
├── datas/
│   ├── code_to_detect/              # Test Data
│   │   ├── bad_data/                #   Known Bad Code
│   │   ├── code_diff/               #   Code Diffs
│   │   └── only_code/               #   Source Code Only
│   ├── RAG_data/rag_data.py         # RAG Rule Documents
│   └── Prompts/                     # Prompt Copies
└── Human_Judge.md                   # Human Evaluation Guide
```
