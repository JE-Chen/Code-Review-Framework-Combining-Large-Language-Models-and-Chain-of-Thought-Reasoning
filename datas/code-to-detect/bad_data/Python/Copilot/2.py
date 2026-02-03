# 測試程式碼：第二批違反 RAG 規則的範例

# 1. 單一函式同時做驗證 / 邏輯 / I/O (違規)
def process_user_input(user_input):
    # 驗證
    if not isinstance(user_input, str):
        print("Invalid input!")  # I/O
        return None
    # 商業邏輯
    if "admin" in user_input:
        print("Access granted")  # I/O
        return True
    else:
        print("Access denied")  # I/O
        return False

# 2. 介面行為依賴隱藏 flag (違規)
hidden_flag = True
def secret_behavior(x):
    if hidden_flag:
        return x * 2
    else:
        return x + 2

# 3. 過度依賴 truthy/falsy 判斷 (違規)
def check_value(val):
    if val:  # 對 None、0、空容器容易出錯
        return "Has value"
    else:
        return "No value"

# 4. Magic number + 命名不清楚 (違規)
def f(x):
    return x * 7 + 13  # 硬編碼數字，函式名稱不清楚

# 5. 註解解釋「做什麼」而不是「為什麼」(違規)
def multiply(a, b):
    # 這個函式會把 a 乘以 b
    return a * b

# 6. 難以測試的設計：濫用 global (違規)
global_config = {"mode": "debug"}

def run_task():
    if global_config["mode"] == "debug":
        print("Running in debug mode")
    else:
        print("Running in normal mode")

# 7. 時間相依邏輯未抽象 (違規)
import time
def timestamped_message(msg):
    return f"{time.time()} - {msg}"

# 8. 未驗證外部輸入 (違規)
def unsafe_eval(user_code):
    return eval(user_code)  # 直接執行外部輸入

# 9. 捕捉 broad exception + 修改輸入參數 (違規)
def risky_update(data):
    try:
        data["count"] += 1
    except Exception:  # 過於寬泛
        data["count"] = 0
    return data