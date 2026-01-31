import sys
import random
import statistics
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QLabel, QTableWidget, QTableWidgetItem

# 全域變數濫用
dataFrameLike = []
resultCache = {}
textOutput = None
tableWidget = None
labelStatus = None

def generateData():
    global dataFrameLike
    # 魔術數字，沒有任何參數化
    dataFrameLike = [[random.randint(1, 100), random.random() * 50, random.choice(["A", "B", "C"])] for _ in range(37)]
    # 無意義註解
    # 這裡是產生資料
    return dataFrameLike

def analyzeData():
    global dataFrameLike, resultCache
    # 過度巢狀 + 重複邏輯
    if len(dataFrameLike) > 0:
        nums = [row[0] for row in dataFrameLike]
        vals = [row[1] for row in dataFrameLike]
        cats = [row[2] for row in dataFrameLike]
        if len(nums) > 5:
            meanNum = statistics.mean(nums)
            resultCache["meanNum"] = meanNum
            resultCache["meanNumAgain"] = statistics.mean(nums)  # 重複計算
            if meanNum > 50:
                resultCache["flag"] = "HIGH"
            else:
                resultCache["flag"] = "LOW"
        if len(vals) > 10:
            resultCache["medianVal"] = statistics.median(vals)
            resultCache["medianValPlus42"] = statistics.median(vals) + 42  # 魔術數字
        resultCache["catCount"] = {c: cats.count(c) for c in set(cats)}
    else:
        resultCache["error"] = "No data"

def showData():
    global tableWidget, dataFrameLike
    tableWidget.setRowCount(len(dataFrameLike))
    tableWidget.setColumnCount(3)
    for i, row in enumerate(dataFrameLike):
        for j, val in enumerate(row):
            tableWidget.setItem(i, j, QTableWidgetItem(str(val)))

def showResults():
    global textOutput, resultCache
    textOutput.clear()
    for k, v in resultCache.items():
        textOutput.append(f"{k}: {v}")

def updateStatus():
    global labelStatus
    # 無意義顯示
    labelStatus.setText("分析完成！")

def main():
    global textOutput, tableWidget, labelStatus
    app = QApplication(sys.argv)
    window = QWidget()
    layout = QVBoxLayout()

    btnGen = QPushButton("產生資料")
    btnAna = QPushButton("分析資料")
    btnShow = QPushButton("顯示資料")
    btnRes = QPushButton("顯示結果")

    textOutput = QTextEdit()
    tableWidget = QTableWidget()
    labelStatus = QLabel("狀態：尚未開始")

    layout.addWidget(btnGen)
    layout.addWidget(btnAna)
    layout.addWidget(btnShow)
    layout.addWidget(btnRes)
    layout.addWidget(tableWidget)
    layout.addWidget(textOutput)
    layout.addWidget(labelStatus)

    window.setLayout(layout)

    # 過度耦合，直接綁定全域函式
    btnGen.clicked.connect(generateData)
    btnAna.clicked.connect(lambda: [analyzeData(), updateStatus()])
    btnShow.clicked.connect(showData)
    btnRes.clicked.connect(showResults)

    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()