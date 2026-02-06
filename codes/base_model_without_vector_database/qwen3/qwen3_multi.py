import gc
import time
import datetime
import torch

from codes.util.qwen3_util import qwen3_ask, load_qwen3_model
from codes.util.prompt_define import question_prompt_define, question_prompt_define_2, system_prompt_define, system_prompt_define_2

model, tokenizer = load_qwen3_model()


# === 多輪推理 ===
for i in range(10):
    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    gc.collect()
    torch.cuda.empty_cache()
    time.sleep(2)

    result = qwen3_ask(question_prompt_define, model, tokenizer)[0]

    print("content:", result)

    with open(f"qwen_response_{i}_1.md", "w", encoding="utf-8") as file:
        file.write(result)

    result = qwen3_ask(question_prompt_define_2 + result, model, tokenizer)[0]

    print("content:", result)

    with open(f"qwen_response_{i}_2.md", "w", encoding="utf-8") as file:
        file.write(result)

    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
