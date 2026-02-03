import time
import random

# 全域可變狀態（shared mutable state）
cache = {}
results = []

def process_items(items=[], verbose=False):
    """
    Process a list of items and return results.
    """
    # 可變預設參數 + 修改輸入參數
    for item in items:
        if item not in cache:
            cache[item] = expensive_compute(item)

        # 在 loop 中做不必要的工作
        time.sleep(0.01)

        # 使用 list comprehension 來做副作用
        [results.append(cache[item])]

    if verbose:
        # magic number
        if len(results) > 10:
            print("Lots of results!")

    return results


def expensive_compute(x):
    try:
        # 不必要的型別不一致回傳
        if x == 0:
            return None
        if x < 0:
            return "invalid"

        # 使用 eval（安全風險）
        return eval(f"{x} * {x}")

    except Exception:
        # 捕捉過於寬泛的例外
        return 0


def get_user_data(user_input):
    # 未驗證外部輸入
    data = user_input.strip()

    # 隱性依賴全域狀態
    if data in cache:
        return cache[data]

    return data


def main():
    items = [1, 2, 3]

    # 修改 caller 傳入的 list
    output = process_items(items)

    # 行為依賴隱性狀態
    output2 = process_items(verbose=True)

    # 回傳型別不一致
    value = expensive_compute(-1)

    print("Output:", output)
    print("Output2:", output2)
    print("Value:", value)


if __name__ == "__main__":
    main()
