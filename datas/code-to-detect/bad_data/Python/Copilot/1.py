# 測試程式碼：故意違反多項 RAG 規則

# 1. 使用可變預設參數 (違規)
def add_item(item, container=[]):
    container.append(item)
    return container

# 2. 全域共享狀態 (違規)
shared_list = []

def append_global(value):
    shared_list.append(value)
    return shared_list

# 3. 修改輸入參數 (違規)
def mutate_input(data):
    for i in range(len(data)):
        data[i] = data[i] * 2
    return data

# 4. 過度巢狀條件 (違規)
def nested_conditions(x):
    if x > 0:
        if x < 10:
            if x % 2 == 0:
                return "small even positive"
            else:
                return "small odd positive"
        else:
            if x < 100:
                return "medium positive"
            else:
                return "large positive"
    else:
        if x == 0:
            return "zero"
        else:
            return "negative"

# 5. 捕捉過於寬泛的例外 (違規)
def risky_division(a, b):
    try:
        return a / b
    except Exception:  # 違規：過於寬泛
        return None

# 6. 回傳型別不一致 (違規)
def inconsistent_return(flag):
    if flag:
        return 42
    else:
        return "forty-two"

# 7. 在 loop 中做重複運算 (違規)
def compute_in_loop(values):
    results = []
    for v in values:
        # 每次都重複計算 len(values)，違規
        if v < len(values):
            results.append(v * 2)
    return results

# 8. 使用 comprehension 做副作用 (違規)
side_effects = [print(i) for i in range(3)]

# 9. Magic number (違規)
def calculate_area(radius):
    return 3.14159 * radius * radius  # 硬編碼 π

# 10. 動態執行程式碼 (違規)
def run_code(code_str):
    return eval(code_str)  # 違規