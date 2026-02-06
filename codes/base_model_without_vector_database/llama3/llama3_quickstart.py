import gc
import os

import torch
from huggingface_hub import login

from codes.util.llama3_util import load_llama3_model, llama3_ask
from codes.util.prompt_define import system_prompt_define, question_prompt_define

login(os.environ["llama3_key"])

llm_pipeline, tokenizer = load_llama3_model()

system_prompt = system_prompt_define
ask_prompt = question_prompt_define

for i in range(10):

    gc.collect()
    torch.cuda.empty_cache()

    result = llama3_ask(system_prompt, ask_prompt, llm_pipeline)

    result = result[0]["generated_text"][-1]["content"]

    print(result)

    with open(f"llama3_response_{i}.md", "w+") as file:
        file.write(result)