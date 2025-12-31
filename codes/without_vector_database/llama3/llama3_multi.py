import gc
import os
import time
import torch

from huggingface_hub import login

from codes.util.llama3_util import llama3_ask, load_llama3_model
from codes.util.prompt_define import question_prompt_define, question_prompt_define_2, system_prompt_define, system_prompt_define_2

# 登入 Hugging Face
login(os.getenv("llama3_key"))

llm_pipeline, tokenizer = load_llama3_model()

# === 多輪推理 ===
for i in range(10):
    gc.collect()
    torch.cuda.empty_cache()
    time.sleep(2)

    result = llama3_ask(system_prompt_define, question_prompt_define, llm_pipeline)

    result = result[0]["generated_text"][-1]["content"]

    print(result)

    with open(f"llama3_response_{i}_1.md", "w", encoding="utf-8") as file:
        file.write(result)

    result = llama3_ask(system_prompt_define_2, question_prompt_define_2 + result, llm_pipeline)

    result = result[0]["generated_text"][-1]["content"]

    # 解析結果
    print(result)

    with open(f"llama3_response_{i}_2.md", "w", encoding="utf-8") as file:
        file.write(result)
