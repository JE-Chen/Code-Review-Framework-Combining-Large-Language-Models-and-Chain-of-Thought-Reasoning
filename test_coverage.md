# 測試覆蓋度：Code-Review-Framework-Combining-Large-Language-Models-and-Chain-of-Thought-Reasoning

測量日期：2026-10-28。數字來自這台 Windows 機器上的一次實測，不是估計，也不是只數檔案。

| 項目 | 內容 |
|---|---|
| 直譯器 | 3.14.4 |
| 直譯器說明 | 專案 .venv |
| 工具 | coverage 7.15.0，`coverage run --branch` |
| 測量範圍 | `prthinker` |
| 測試路徑 | `tests` |
| 命令 | `python -m coverage run --branch --source=prthinker -m pytest tests` |
| 敘述覆蓋 | 90.26%（14188 / 15719） |
| 分支覆蓋 | 82.79%（3222 / 3892） |
| 測試結果 | 2488 passed in 87.50s (0:01:27) |
| 耗時 | 92.9 秒 |

敘述覆蓋是執行到的敘述數除以全部敘述數。分支覆蓋是執行到的分支數除以全部分支數。兩者分開算，沒有把分支混進敘述百分比。

## 這次怎麼量

只測量發行套件 `prthinker`。`codes/`、`datas/`、`paper/` 不在這次的 source 裡。

## 覆蓋較低的檔案

只列這次測量裡敘述覆蓋最低的檔案，最多 12 個。

| 檔案 | 敘述覆蓋 | 已覆蓋 / 敘述 |
|---|---:|---:|
| `prthinker/__main__.py` | 0.0% | 0 / 3 |
| `prthinker/prompts/CRSCORE/crscore_cot_evaluation.py` | 0.0% | 0 / 1 |
| `prthinker/prompts/CRSCORE/crscore_llm_as_judge.py` | 0.0% | 0 / 1 |
| `prthinker/prompts/finding_self_review.py` | 0.0% | 0 / 1 |
| `prthinker/prompts/judge.py` | 0.0% | 0 / 1 |
| `prthinker/prompts/judge_single_review.py` | 0.0% | 0 / 1 |
| `prthinker/prompts/step_by_step_analysis.py` | 0.0% | 0 / 1 |
| `prthinker/review_presets.py` | 21.43% | 6 / 28 |
| `prthinker/otel.py` | 35.29% | 18 / 51 |
| `prthinker/cli_review_overall_summary.py` | 36.51% | 23 / 63 |
| `prthinker/cli_review.py` | 46.27% | 180 / 389 |
| `prthinker/mcp_server.py` | 47.01% | 55 / 117 |
