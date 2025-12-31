import gc

import torch

from codes.util.qwen3_util import load_qwen3_model, qwen3_ask
from codes.util.prompt_define import system_prompt_define, question_prompt_define

system_prompt = system_prompt_define
ask_prompt = question_prompt_define

model, tokenizer = load_qwen3_model()

for i in range(10):

    gc.collect()
    torch.cuda.empty_cache()

    result = qwen3_ask(system_prompt, ask_prompt, model, tokenizer)[0]

    print("content: \n", result)

    with open(f"qwen3_response_{i}.md", "w+") as file:
        file.write(result)