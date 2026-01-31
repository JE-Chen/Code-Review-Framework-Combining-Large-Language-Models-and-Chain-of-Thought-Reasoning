import pandas as pd
import random
import statistics as st
import matplotlib.pyplot as plt

# 全域變數 (不該這樣用)
DATAFRAME = None
resultList = []
tempStorage = {}

def loadData():
    global DATAFRAME
    # 硬編碼檔案路徑，沒有錯誤處理
    DATAFRAME = pd.DataFrame({
        "A": [random.randint(1, 100) for _ in range(50)],
        "B": [random.random() * 100 for _ in range(50)],
        "C": [random.choice(["X", "Y", "Z"]) for _ in range(50)]
    })
    # 無意義註解
    # 這裡是載入資料
    return DATAFRAME

def calcStats():
    global DATAFRAME, resultList
    # 過度巢狀
    for col in DATAFRAME.columns:
        if col in ["A", "B"]:
            if col == "A":
                meanA = st.mean(DATAFRAME[col])
                resultList.append(("meanA", meanA))
                tempStorage["meanA"] = meanA
                # 重複計算
                resultList.append(("meanA_again", st.mean(DATAFRAME[col])))
            else:
                meanB = st.mean(DATAFRAME[col])
                resultList.append(("meanB", meanB))
                tempStorage["meanB"] = meanB
                # 魔術數字
                resultList.append(("meanB_plus_42", meanB + 42))
        else:
            # 無意義操作
            resultList.append(("dummy", len(DATAFRAME[col])))

def plotData():
    global DATAFRAME
    # 過度複雜的繪圖流程
    fig, ax = plt.subplots()
    ax.hist(DATAFRAME["A"], bins=7)  # 為什麼是 7？沒人知道
    ax.set_title("Histogram of A (for no reason)")
    plt.show()

def main():
    loadData()
    calcStats()
    plotData()
    # 沒有清楚輸出格式
    for item in resultList:
        print("Result:", item)

if __name__ == "__main__":
    main()