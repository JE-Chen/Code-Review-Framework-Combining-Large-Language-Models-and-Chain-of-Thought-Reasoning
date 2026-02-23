|                  |                  CRSCORE                  |                    CRSCORE++                     |             Our              |
|:----------------:|:-----------------------------------------:|:------------------------------------------------:|:----------------------------:|
|  Max New Tokens  |                     ?                     |                        ?                         |            32768             |
|    Base Model    |            Magicoder-S-DS-6.7B            |            Qwen2.5-Coder-7B-Instruct             | Qwen3-Coder-30B-A3B-Instruct |
|  Fine-tune data  | CodeReviewer dataset (1k samples) & GPT-4 | CodeReviewer dataset (22k samples) & GPT-4o-mini |       GPT-5 & Copilot        |
|   LLM as Judge   |                  GPT3.5                   |                   GPT-4o-mini                    |       GPT-5 & Copilot        |
| Chain of thought |                     N                     |                        Y                         |              Y               |
|     scoring      |     BLEU. traditional method & GPT-4      |                   GPT-4o-mini                    |       GPT-5 & Copilot        |
|   Testing data   |            codereview dataset             |                codereview dataset                |      AI generation code      |
|       RAG        |                     N                     |                        N                         |              Y               |

|                             | CRSCORE | CRSCORE++ |   Our    |
|:---------------------------:|:-------:|:---------:|:--------:|
|           SEQ_LEN           |    ?    |   1024    |   1024   |
|      MICRO_BATCH_SIZE       |    ?    |     2     |    1     |
| GRADIENT_ACCUMULATION_STEPS |    ?    |     ?     |    64    |
|         NUM_EPOCHS          |    ?    |     2     |    3     |
|        LEARNING_RATE        |    ?    |   2e-5    |   2e-5   |
|        WARMUP_RATIO         |    ?    |     ?     |   0.1    |
|        WEIGHT_DECAY         |    ?    |    0.1    |   0.01   |
|           LORA_R            |    ?    |     ?     |    64    |
|         LORA_ALPHA          |    ?    |     ?     |    64    |
|        LORA_DROPOUT         |    ?    |     ?     |   0.1    |
|      Traning hardware       |    ?    | A100 * 2  | L40S * 2 |

| 參數                              | 意義說明                       |
|---------------------------------|----------------------------|
| **SEQ_LEN**                     | 最大序列長度，模型一次能處理的 token 數量   |
| **MICRO_BATCH_SIZE**            | 單 GPU 一次前向/反向傳遞的樣本數        |
| **GRADIENT_ACCUMULATION_STEPS** | 梯度累積步數，用來模擬更大 batch size   |
| **NUM_EPOCHS**                  | 訓練輪數，整個資料集被完整訓練的次數         |
| **LEARNING_RATE**               | 學習率，控制每次梯度更新幅度             |
| **WARMUP_RATIO**                | 學習率預熱比例，避免初期更新過大           |
| **WEIGHT_DECAY**                | 權重衰減 (L2 正則化)，防止過擬合        |
| **LORA_R**                      | LoRA rank，決定低秩矩陣維度         |
| **LORA_ALPHA**                  | LoRA 縮放，調整更新幅度             |
| **LORA_DROPOUT**                | LoRA dropout 機率，增加隨機性避免過擬合 |
| **Training hardware**           | 訓練所用硬體資源 (GPU 型號與數量)       |

|      | CRSCORE                                                          | CRSCORE ++                                                                                                               | Our                                                                                                                              |
|------|------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------|
| 評分維度 | Comprehensiveness（完整性）,<br/>Conciseness（精簡性）,<br/>Relevance（相關性） | Comprehensiveness（完整性）, <br/>Conciseness（精簡性）, <br/>Relevance（相關性）                                                       | Readability, <br/>Constructiveness (Maintainability), <br/>Correctness,<br/> Conciseness,<br/> Comprehensiveness,<br/> Relevance |
| 評分分數 | 1-5                                                              | 1-5                                                                                                                      | 1-100                                                                                                                            |
| 評分筆數 | 5700 個生成, 2900 個人工評論                                             | 20888 CodeReview dataset 抽取 5000 筆， <br>各生成 20 筆評論,<br/> 挑選 Python 33 筆 <br/>Java 33 筆 <br/>JavaScript 33 筆，<br/>來進行人工驗證 | 22 筆 GPT-5 跟 22 筆 Copilot 產生的程式碼， <br> 每筆資料各生成 8 筆評論， <br>總共352則評論                                                               
