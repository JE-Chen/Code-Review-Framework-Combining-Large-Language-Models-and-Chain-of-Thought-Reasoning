# 這是一個示範程式，雖然能執行，但充滿程式碼異味
# 程式碼異味包含：過度複雜、命名不清、重複邏輯、魔法數字、過度巢狀、沒有效率的寫法

def doSomething(a, b, c, d, e, f, g, h, i, j):
    # 函式參數過多，難以維護
    result = 0
    if a > 10:
        if b < 5:
            if c == 3:
                if d != 0:
                    result = (a * b * c) / d
                else:
                    result = 999999  # 魔法數字
            else:
                result = a + b + c + d
        else:
            if e == "yes":
                result = len(e) * 1234  # 魔法數字
            else:
                result = 42  # 又一個魔法數字
    else:
        if f == "no":
            result = 123456789  # 過大的魔法數字
        else:
            result = -1  # 不明意義的回傳值
    return result

# 全域變數濫用
dataList = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

def processData():
    # 使用不清楚的變數命名
    x = 0
    for k in range(len(dataList)):
        # 重複邏輯，沒有抽取成函式
        if dataList[k] % 2 == 0:
            x += dataList[k] * 2
        else:
            x += dataList[k] * 3
    return x

def main():
    # 過度複雜的呼叫，參數硬塞
    val = doSomething(11, 4, 3, 2, "yes", "no", None, None, None, None)
    print("Result:", val)

    # 沒有錯誤處理，直接執行
    print("Process:", processData())

    # 過度巢狀的 if-else
    y = 5
    if y > 0:
        if y < 10:
            if y % 2 == 1:
                print("Odd and small")
            else:
                print("Even and small")
        else:
            if y == 10:
                print("Exactly ten")
            else:
                print("Greater than ten")
    else:
        print("Non-positive")

if __name__ == "__main__":
    main()