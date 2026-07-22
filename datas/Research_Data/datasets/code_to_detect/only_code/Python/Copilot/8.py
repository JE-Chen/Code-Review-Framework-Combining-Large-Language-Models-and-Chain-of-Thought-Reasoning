import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QTextEdit

class BaseWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Base Window")
        self.setGeometry(100, 100, 600, 400)

class CustomWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.btnA = QPushButton("Click Me A")
        self.btnB = QPushButton("Click Me B")
        self.labelX = QLabel("Initial Text")
        self.textArea = QTextEdit()

        vbox = QVBoxLayout()
        hbox = QHBoxLayout()
        hbox.addWidget(self.btnA)
        hbox.addWidget(self.btnB)
        vbox.addLayout(hbox)
        vbox.addWidget(self.labelX)
        vbox.addWidget(self.textArea)
        self.setLayout(vbox)

        self.btnA.clicked.connect(self.handle_btnA)
        self.btnB.clicked.connect(self.handle_btnB)

    def handle_btnA(self):
        text = self.textArea.toPlainText()
        if len(text) > 0:
            self.labelX.setText("Length: " + str(len(text)))
        else:
            self.labelX.setText("Empty!")

    def handle_btnB(self):
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
        self.central = CustomWidget()
        self.setCentralWidget(self.central)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()