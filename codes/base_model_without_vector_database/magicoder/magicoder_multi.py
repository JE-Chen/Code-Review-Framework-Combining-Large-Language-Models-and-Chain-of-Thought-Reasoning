import gc
import time
import torch

from codes.util.magicoder_util import load_magicoder_model, magicoder_ask
from codes.util.prompt_define import question_prompt_define, system_prompt_define, question_prompt_define_2, system_prompt_define_2


# === 推理迴圈 ===
MAGICODER_PROMPT = """
{system_prompt_define}

@@ Instruction
{instruction}

@@ Response
"""

model, tokenizer, device = load_magicoder_model()

for i in range(10):
    gc.collect()
    torch.cuda.empty_cache()
    time.sleep(2)


    _prompt = MAGICODER_PROMPT

    _prompt = _prompt.format(system_prompt_define=system_prompt_define, instruction=question_prompt_define)

    result = magicoder_ask(_prompt, model, tokenizer, device)

    print(result)

    with open(f"magicoder_response_{i}_{1}.md", "w", encoding="utf-8") as file:
        file.write(result)

    _prompt = MAGICODER_PROMPT

    _prompt = _prompt.format(system_prompt_define=system_prompt_define_2,
                            instruction=question_prompt_define_2 + result)

    result = magicoder_ask(_prompt, model, tokenizer, device)

    print(result)

    with open(f"magicoder_response_{i}_{2}.md", "w", encoding="utf-8") as file:
        file.write(result)