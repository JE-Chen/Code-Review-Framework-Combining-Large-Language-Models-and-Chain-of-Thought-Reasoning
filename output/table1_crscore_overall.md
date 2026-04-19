# 表1 採用 CRSCORE++ 方法的整體評估

| 維度 | Ours | CRSCORE++ |
| --- | --- | --- |
| comprehensiveness | 0.86 | 0.67 |
| conciseness | 0.64 | 0.57 |
| relevance | 0.83 | 0.63 |

## 解釋

本表比較本研究方法 (Ours) 與 CRSCORE++ 基準方法在三個面向上的得分。本方法在 **comprehensiveness（0.86 vs 0.67）**、**conciseness（0.64 vs 0.57）**、**relevance（0.83 vs 0.63）** 三項皆顯著勝出：

本方法在覆蓋度、精煉度與相關性三項皆優於 CRSCORE++，顯示 CoT 拆解、RAG 規則注入與 LoRA 微調的協同作用，能在涵蓋更多問題的同時兼顧精簡與聚焦。
