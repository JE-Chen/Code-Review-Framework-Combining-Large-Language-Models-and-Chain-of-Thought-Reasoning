# 這是一個「看起來很認真」的使用者資料處理程式
# 但裡面充滿設計異味 🤢

import json
import os
import random

# ❌ 硬編碼路徑（Hard-coded path）
DATA_FILE = "./data/users.json"


# ❌ 類別幾乎沒有行為（Anemic Domain Model）
class User:
    def __init__(self, name, age, score, active):
        self.name = name
        self.age = age
        self.score = score
        self.active = active


# ❌ 無意義的全域快取（Hidden Dependency + Global State）
_cache = {}


# ❌ 函式責任不清：又讀檔、又 parse、又做 business logic（Low Cohesion）
def loadAndProcessUsers(flag=True, debug=False, verbose=False):
    users = []

    # ❌ 時序耦合（Temporal Coupling）：必須先存在檔案才能繼續
    if not os.path.exists(DATA_FILE):
        # ❌ 用 print 當錯誤處理（Poor Error Handling）
        print("File not found, but continue anyway...")
        return []

    f = open(DATA_FILE, "r")
    text = f.read()
    f.close()

    # ❌ 直接吞掉所有例外（Overly Broad Exception）
    try:
        raw = json.loads(text)
    except:
        raw = []

    # ❌ 不必要的中間資料結構（Unnecessary Data Transformation）
    temp = []
    for r in raw:
        temp.append(r)

    # ❌ 重複遍歷資料（Inefficient Looping）
    for item in temp:
        name = item.get("name", "")
        age = item.get("age", 0)
        score = item.get("score", 0)
        active = item.get("active", False)

        # ❌ Boolean Blindness（只靠 True / False，語意不清）
        if flag:
            active = True

        u = User(name, age, score, active)
        users.append(u)

    # ❌ 特性嫉妒（Feature Envy）：外部函式操作 User 內部資料過多
    result = []
    for u in users:
        # ❌ 神秘規則（Magic Business Rule）
        if u.active and u.score > 60 and u.age >= 18:
            result.append(u)

    # ❌ 除錯旗標污染商業邏輯（Flag Argument）
    if debug:
        print("Loaded users:", len(result))

    if verbose:
        for u in result:
            print(u.name, u.age, u.score, u.active)

    # ❌ 把結果塞進全域快取（Hidden Side Effect）
    _cache["last"] = result

    return result


# ❌ 函式名稱與行為不符（Misleading Name）
def calculateAverage(users):
    total = 0
    count = 0

    # ❌ Reinventing the wheel（明明可以用 sum / len）
    for u in users:
        total = total + u.score
        count = count + 1

    # ❌ 無意義的防呆（永遠不會發生）
    if count == 0:
        return 0

    avg = total / count

    # ❌ 不必要的精度轉換（Pointless Conversion）
    avg = float(str(avg))

    return avg


# ❌ 回傳型別不一致（Inconsistent Return Type）
def getTopUser(users, allow_random=False):
    if len(users) == 0:
        return None

    best = users[0]

    for u in users:
        if u.score > best.score:
            best = u

    # ❌ 加入隨機行為破壞可預測性（Non-deterministic Behavior）
    if allow_random and random.random() > 0.7:
        return random.choice(users)

    # ❌ 有時回傳物件，有時回傳 dict（Type Inconsistency）
    if best.score > 90:
        return {"name": best.name, "score": best.score}

    return best


# ❌ 資料團塊（Data Clumps）：一堆參數其實應該包成物件
def formatUser(name, age, score, active, prefix="", suffix=""):
    # ❌ 註解掉的殭屍程式碼（Commented-out Dead Code）
    # if active:
    #     status = "ACTIVE"
    # else:
    #     status = "INACTIVE"

    status = "ACTIVE" if active else "INACTIVE"

    # ❌ 字串組合風格混亂（Inconsistent Style）
    text = prefix + name + " | " + str(age) + " | " + str(score) + " | " + status + suffix
    return text


# ❌ 主要流程過度依賴隱藏狀態（Hidden Coupling）
def mainProcess():
    users = loadAndProcessUsers(flag=False, debug=True, verbose=False)

    avg = calculateAverage(users)

    top = getTopUser(users, allow_random=True)

    print("Average score:", avg)

    # ❌ 大量 isinstance 檢查（Type Checking Smell）
    if isinstance(top, dict):
        print("Top user (dict):", top["name"], top["score"])
    elif isinstance(top, User):
        line = formatUser(top.name, top.age, top.score, top.active)
        print("Top user (obj):", line)
    else:
        print("No top user")

    # ❌ 依賴全域快取（Hidden Dependency）
    if "last" in _cache:
        print("Cached users:", len(_cache["last"]))


# 主程式入口
if __name__ == "__main__":
    # ❌ 神秘初始化資料（Magic Initialization）
    if not os.path.exists("./data"):
        os.makedirs("./data")

    # 建立假資料，確保程式能跑
    fake = [
        {"name": "Alice", "age": 20, "score": 80, "active": True},
        {"name": "Bob", "age": 17, "score": 95, "active": True},
        {"name": "Cathy", "age": 30, "score": 60, "active": False},
    ]

    with open(DATA_FILE, "w") as f:
        f.write(json.dumps(fake))

    mainProcess()
