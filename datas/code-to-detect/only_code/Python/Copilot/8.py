# PySide6 範例程式碼：能執行但充滿程式碼異味
# 程式碼異味包含：過度使用繼承、多層 GUI 類別、結構冗長、命名混亂、魔法數字

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QTextEdit

# 過度使用繼承：其實不需要這麼多層級
class BaseWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Base Window")
        self.setGeometry(100, 100, 600, 400)  # 魔法數字

class CustomWidget(QWidget):
    def __init__(self):
        super().__init__()
        # 命名混亂：btnA、btnB 沒有語意
        self.btnA = QPushButton("Click Me A")
        self.btnB = QPushButton("Click Me B")
        self.labelX = QLabel("Initial Text")
        self.textArea = QTextEdit()

        # 過度複雜的版面配置
        vbox = QVBoxLayout()
        hbox = QHBoxLayout()
        hbox.addWidget(self.btnA)
        hbox.addWidget(self.btnB)
        vbox.addLayout(hbox)
        vbox.addWidget(self.labelX)
        vbox.addWidget(self.textArea)
        self.setLayout(vbox)

        # 事件綁定
        self.btnA.clicked.connect(self.handle_btnA)
        self.btnB.clicked.connect(self.handle_btnB)

    def handle_btnA(self):
        # 邏輯塞在事件處理器裡，沒有抽象化
        text = self.textArea.toPlainText()
        if len(text) > 0:
            self.labelX.setText("Length: " + str(len(text)))
        else:
            self.labelX.setText("Empty!")  # 沒有錯誤處理策略

    def handle_btnB(self):
        # 過度巢狀的邏輯
        text = self.textArea.toPlainText()
        if text:
            if len(text) < 5:
                self.labelX.setText("Short")
            else:
                if len(text) < 10:
                    self.labelX.setText("Medium")
                else:
                    if len(text) < 20:
                        self.labelX.setText("Long")
                    else:
                        self.labelX.setText("Very Long")
        else:
            self.labelX.setText("No Input")

class MainWindow(BaseWindow):
    def __init__(self):
        super().__init__()
        # 過度包裝：其實可以直接用 QWidget
        self.central = CustomWidget()
        self.setCentralWidget(self.central)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()