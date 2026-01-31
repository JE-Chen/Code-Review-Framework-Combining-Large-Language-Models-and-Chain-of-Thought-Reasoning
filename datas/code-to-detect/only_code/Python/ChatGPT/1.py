# 這個檔案「看起來很努力在工作」，但設計上問題一堆 😅

import math
import time

# ❌ 全域變數濫用（Global State）
total_result = 0


# ❌ 函式名稱不清楚，參數過多（Long Parameter List + Poor Naming）
def doStuff(a, b, c, d, e, f, g, h, i, j):
    # ❌ 魔術數字（Magic Numbers）
    if a > 10:
        x = a * 3.14159
    else:
        x = a * 2.71828

    # ❌ 重複邏輯（Duplicated Code）
    if b == "square":
        y = c * c
    elif b == "circle":
        y = 3.14159 * c * c
    else:
        y = c

    # ❌ 不必要的巢狀結構（Deep Nesting）
    if d:
        if e:
            if f:
                if g:
                    if h:
                        z = x + y
                    else:
                        z = x - y
                else:
                    z = x * y
            else:
                if y != 0:
                    z = x / y
                else:
                    z = 0
        else:
            z = x
    else:
        z = y

    # ❌ 沒意義的暫存變數（Unnecessary Temporary Variables）
    temp1 = z + 1
    temp2 = temp1 - 1
    result = temp2

    # ❌ 修改全域狀態（Side Effects）
    global total_result
    total_result += result

    # ❌ 無意義的 sleep（Artificial Delay）
    time.sleep(0.01)

    # ❌ 參數根本沒用到（Unused Parameters）
    if i or j:
        pass

    return result


# ❌ God Function：一次做太多事情
def processEverything(data):
    results = []

    # ❌ for 迴圈內邏輯過於複雜
    for item in data:
        # ❌ 型別檢查混亂（Type Checking Instead of Polymorphism）
        if type(item) == int:
            a = item
        elif type(item) == float:
            a = int(item)
        elif type(item) == str:
            try:
                a = int(item)
            except:
                a = 0
        else:
            a = 0

        # ❌ 重複邏輯 again（Duplicated Code Again）
        if a % 2 == 0:
            shape = "square"
        else:
            shape = "circle"

        # ❌ 意義不明的布林旗標
        flag1 = True
        flag2 = False
        flag3 = True
        flag4 = True
        flag5 = False

        r = doStuff(
            a, shape, a,
            flag1, flag2, flag3, flag4, flag5,
            None, None
        )

        # ❌ 無意義的條件判斷
        if r >= 0:
            results.append(r)
        else:
            results.append(0)

    # ❌ 沒必要的重新計算
    total = 0
    for v in results:
        total += v

    # ❌ 影子變數（Shadowing built-in name）
    sum = total

    # ❌ 不必要的格式轉換
    final_result = float(str(sum))

    return final_result


# ❌ 可變預設參數（Mutable Default Argument）— 經典地雷
def collectValues(x, bucket=[]):
    bucket.append(x)
    return bucket


# 主程式區
if __name__ == "__main__":
    data = [1, 2, "3", 4.5, "bad", 7]

    output = processEverything(data)

    print("Final:", output)

    # ❌ collectValues 的副作用示範
    print(collectValues(1))
    print(collectValues(2))
    print(collectValues(3))

    # ❌ 依賴全域狀態
    print("Global total_result:", total_result)
