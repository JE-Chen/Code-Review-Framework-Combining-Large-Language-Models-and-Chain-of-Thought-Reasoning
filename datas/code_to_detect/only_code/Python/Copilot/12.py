import pandas as pd
import random
import statistics as st
import matplotlib.pyplot as plt

DATAFRAME = None
resultList = []
tempStorage = {}

def loadData():
    global DATAFRAME
    DATAFRAME = pd.DataFrame({
        "A": [random.randint(1, 100) for _ in range(50)],
        "B": [random.random() * 100 for _ in range(50)],
        "C": [random.choice(["X", "Y", "Z"]) for _ in range(50)]
    })
    return DATAFRAME

def calcStats():
    global DATAFRAME, resultList
    for col in DATAFRAME.columns:
        if col in ["A", "B"]:
            if col == "A":
                meanA = st.mean(DATAFRAME[col])
                resultList.append(("meanA", meanA))
                tempStorage["meanA"] = meanA
                resultList.append(("meanA_again", st.mean(DATAFRAME[col])))
            else:
                meanB = st.mean(DATAFRAME[col])
                resultList.append(("meanB", meanB))
                tempStorage["meanB"] = meanB
                resultList.append(("meanB_plus_42", meanB + 42))
        else:
            resultList.append(("dummy", len(DATAFRAME[col])))

def plotData():
    global DATAFRAME
    fig, ax = plt.subplots()
    ax.hist(DATAFRAME["A"], bins=7)
    ax.set_title("Histogram of A (for no reason)")
    plt.show()

def main():
    loadData()
    calcStats()
    plotData()
    for item in resultList:
        print("Result:", item)

if __name__ == "__main__":
    main()