# Python 資料結構範例程式碼：能執行但充滿程式碼異味
# 程式碼異味包含：過度複雜的資料結構、命名混亂、重複邏輯、魔法數字、效率低落

# 過度複雜的巢狀資料結構
DATA = {
    "users": [
        {"id": 1, "name": "Alice", "info": {"age": 25, "scores": [10, 20, 30]}},
        {"id": 2, "name": "Bob", "info": {"age": 30, "scores": [15, 25, 35]}},
        {"id": 3, "name": "Charlie", "info": {"age": 35, "scores": [5, 50, 100]}},
    ],
    "config": {
        "threshold": 50,  # 魔法數字
        "mode": "X",
        "flags": [True, False, True]
    },
    "misc": [
        {"key": "alpha", "value": 123},
        {"key": "beta", "value": 456},
        {"key": "gamma", "value": 789}
    ]
}

def calculate_average_scores():
    # 重複邏輯：每個使用者都做相同處理，沒有抽象化
    results = []
    for user in DATA["users"]:
        scores = user["info"]["scores"]
        total = 0
        for s in scores:
            total += s
        avg = total / len(scores)
        results.append({"id": user["id"], "avg": avg})
    return results

def filter_high_scores():
    # 魔法數字直接硬編碼
    high_scores = []
    for user in DATA["users"]:
        for s in user["info"]["scores"]:
            if s > 40:  # 魔法數字
                high_scores.append({"user": user["name"], "score": s})
    return high_scores

def process_misc():
    # 過度複雜的邏輯，硬塞在一個函式裡
    result = {}
    for item in DATA["misc"]:
        if item["value"] % 2 == 0:
            if item["value"] > DATA["config"]["threshold"]:
                result[item["key"]] = "Large Even"
            else:
                result[item["key"]] = "Small Even"
        else:
            if item["value"] > DATA["config"]["threshold"]:
                result[item["key"]] = "Large Odd"
            else:
                result[item["key"]] = "Small Odd"
    return result

def main():
    averages = calculate_average_scores()
    print("Averages:", averages)

    highs = filter_high_scores()
    print("High Scores:", highs)

    misc_result = process_misc()
    print("Misc Result:", misc_result)

    # 過度巢狀的邏輯
    if DATA["config"]["mode"] == "X":
        if DATA["config"]["flags"][0]:
            print("Mode X with flag True")
        else:
            if DATA["config"]["flags"][1]:
                print("Mode X with second flag True")
            else:
                print("Mode X with all flags False")
    else:
        print("Other mode")

if __name__ == "__main__":
    main()