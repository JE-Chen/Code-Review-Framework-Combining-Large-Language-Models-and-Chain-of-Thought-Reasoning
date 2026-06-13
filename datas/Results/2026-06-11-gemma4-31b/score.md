# gemma4-31b LoRA — LLM-as-a-Judge scores (2026-06-12)

44 cases. One judgment per case per protocol, produced by independent
judge agents (Claude). Per-case tuples: `all_crscore_score.md`,
`all_our_score.md`, and `cot_<case>/{crscore_score.md,our_score.md}`.

> Judge-model caveat: CRSCORE++ was judged by GPT-4o-mini and the
> qwen3-coder-30b run by GPT-5; the gemma4 column below was judged by
> Claude. Cross-column comparisons therefore confound model quality with
> judge leniency — treat them as indicative, not conclusive. Notably the
> Claude judge saturated comprehensiveness (5/5 on all 44 cases).

## CRSCORE protocol

| normalize 0~1,1=0.2 | CRSCORE++ | Our (qwen3-coder-30b) | gemma4-31b |
|:-------------------:|:---------:|:---------------------:|:----------:|
|  comprehensiveness  |   0.67    |         0.86          |  **1.00**  |
|     conciseness     |   0.57    |         0.64          |  **0.79**  |
|      relevance      |   0.63    |         0.83          |  **0.86**  |

| normalize 0~100,1=20 | CRSCORE++ | Our (qwen3-coder-30b) | gemma4-31b |
|:--------------------:|:---------:|:---------------------:|:----------:|
|  comprehensiveness   |    67     |          86           |  **100**   |
|     conciseness      |    57     |          64           |   **79**   |
|      relevance       |    63     |          83           |   **86**   |

## Our judge protocol (five dimensions, 1–100)

| dimension                                        | gemma4-31b |
|:------------------------------------------------:|:----------:|
| Readability                                      |    87.1    |
| Constructiveness (Maintainability)               |    87.2    |
| Correctness                                      |    79.5    |
| Multi-Review Coverage / Extractability           |    84.1    |
| Comprehensiveness                                |    87.5    |
| **Overall average**                              |  **85.1**  |

Recurring judge feedback: reviews are comprehensive and actionable but
repeat the same findings across the four report sections (conciseness
cost), and correctness is the weakest dimension — occasional overstated
or imprecise claims (e.g. `except Exception` / KeyboardInterrupt
conflation, "memory leak" hyperbole).
