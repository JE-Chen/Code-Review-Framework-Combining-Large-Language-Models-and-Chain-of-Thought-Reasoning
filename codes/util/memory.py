# === 自動偵測 GPU 與顯存 ===
import torch


def get_max_memory(reserve_gib=1.5, cap_ratio=0.92):
    max_memory = {}
    if torch.cuda.is_available():
        for i in range(torch.cuda.device_count()):
            total_gib = torch.cuda.get_device_properties(i).total_memory / (1024**3)
            cap_gib = max(total_gib * cap_ratio, total_gib - reserve_gib)
            cap_gib = max(1.0, round(cap_gib, 2))
            max_memory[i] = f"{cap_gib}GiB"
    return max_memory