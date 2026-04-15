# Code Review Framework - Architecture Diagram

## System Overview

```mermaid
graph TB
    CODE["Source Code<br/>ChatGPT / Copilot Generated"]
    DT["bad_data · code_diff · only_code"]
    CODE --> DT

    RAG_DATA["Rule Documents"] --> EMB["Qwen3-Embedding-4B"]
    CODE --> EMB
    EMB --> FAISS["FAISS Vector Index"]
    FAISS -->|"threshold ≥ 0.7"| RULES["Retrieved Rules"]

    RULES --> GR["7 Review Standards<br/>+ RAG Rules Injection"]

    DT --> COT & SKILLS & SINGLE
    GR --> COT & SKILLS

    COT["CoT Pipeline<br/>Summary → Review → Linter → Smell → Total"]
    SKILLS["Skills Pipeline<br/>Explainer + Review"]
    SINGLE["Single Prompt Baseline"]

    COT --> QWEN
    SKILLS --> QWEN
    SINGLE --> QWEN

    LORA["LoRA Adapter"] --> QWEN["Qwen3-Coder-30B-A3B<br/>4-bit Quantization"]

    QWEN -->|"Review Results"| JUDGE["LLM-as-Judge<br/>5 Dimensions Scoring"]
    QWEN -->|"Review Results"| CRSCORE["CRScore Evaluation"]
    QWEN -->|"Review Results"| HUMAN["Human Judge 人工評估"]

    style CODE fill:#e1f5fe,stroke:#0288d1
    style DT fill:#e1f5fe,stroke:#0288d1
    style RAG_DATA fill:#f3e5f5,stroke:#7b1fa2
    style EMB fill:#f3e5f5,stroke:#7b1fa2
    style FAISS fill:#f3e5f5,stroke:#7b1fa2
    style RULES fill:#f3e5f5,stroke:#7b1fa2
    style GR fill:#f1f8e9,stroke:#558b2f
    style COT fill:#e8f5e9,stroke:#2e7d32
    style SKILLS fill:#fce4ec,stroke:#c62828
    style SINGLE fill:#fff9c4,stroke:#f9a825
    style LORA fill:#fff3e0,stroke:#ef6c00
    style QWEN fill:#fff3e0,stroke:#ef6c00
    style JUDGE fill:#efebe9,stroke:#4e342e
    style CRSCORE fill:#efebe9,stroke:#4e342e
    style HUMAN fill:#efebe9,stroke:#4e342e
```

## CoT Code Review Detailed Flow

```mermaid
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

    style COT fill:#e8f5e9
    style TS fill:#fff3e0
    style JUDGE fill:#efebe9
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
