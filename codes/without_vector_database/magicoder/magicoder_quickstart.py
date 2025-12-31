import gc

import torch

from codes.util.magicoder_util import load_magicoder_model, magicoder_ask
from codes.util.prompt_define import system_prompt_define, question_prompt_define

model, tokenizer, device = load_magicoder_model()

MAGICODER_PROMPT = """
{system_prompt_define}

@@ Instruction
{instruction}

@@ Response
"""

system_prompt = system_prompt_define
ask_prompt = question_prompt_define

for i in range(10):

    gc.collect()
    torch.cuda.empty_cache()

    _prompt = MAGICODER_PROMPT

    _prompt = _prompt.format(system_prompt_define=system_prompt, instruction=ask_prompt)

    result = magicoder_ask(_prompt, model, tokenizer, device)

    print(result)

    with open(f"magicoder_response_{i}.md", "w+") as file:
        file.write(result)