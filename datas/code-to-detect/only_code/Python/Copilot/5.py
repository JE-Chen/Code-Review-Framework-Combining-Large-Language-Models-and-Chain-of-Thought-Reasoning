# 這是一個示範程式，雖然能執行，但充滿程式碼異味
# 程式碼異味包含：過度使用全域變數、狀態混亂、函式耦合過高、命名不清楚、魔法數字

# 全域變數濫用
GLOBAL_STATE = {
    "counter": 0,
    "data": [],
    "mode": "default",
    "threshold": 77,  # 魔法數字
    "flag": False
}

def init_data():
    # 初始化資料但直接寫入全域變數
    GLOBAL_STATE["data"] = [i for i in range(1, 21)]
    GLOBAL_STATE["counter"] = len(GLOBAL_STATE["data"])

def increment_counter():
    # 過度依賴全域狀態
    GLOBAL_STATE["counter"] += 1
    return GLOBAL_STATE["counter"]

def toggle_flag():
    # 狀態混亂：flag 被隨意切換
    GLOBAL_STATE["flag"] = not GLOBAL_STATE["flag"]
    return GLOBAL_STATE["flag"]

def process_items():
    # 過度複雜的邏輯，直接操作全域變數
    results = []
    for item in GLOBAL_STATE["data"]:
        if GLOBAL_STATE["flag"]:
            if item % 2 == 0:
                results.append(item * 2)
            else:
                results.append(item * 3)
        else:
            if item > GLOBAL_STATE["threshold"]:
                results.append(item - GLOBAL_STATE["threshold"])
            else:
                results.append(item + GLOBAL_STATE["threshold"])
    return results

def reset_state():
    # 無意義的重設函式
    GLOBAL_STATE["counter"] = 0
    GLOBAL_STATE["data"] = []
    GLOBAL_STATE["mode"] = "reset"
    GLOBAL_STATE["flag"] = False

def main():
    init_data()
    print("Initial counter:", GLOBAL_STATE["counter"])

    toggle_flag()
    print("Flag status:", GLOBAL_STATE["flag"])

    results = process_items()
    print("Processed results:", results)

    increment_counter()
    print("Counter after increment:", GLOBAL_STATE["counter"])

    reset_state()
    print("State after reset:", GLOBAL_STATE)

if __name__ == "__main__":
    main()