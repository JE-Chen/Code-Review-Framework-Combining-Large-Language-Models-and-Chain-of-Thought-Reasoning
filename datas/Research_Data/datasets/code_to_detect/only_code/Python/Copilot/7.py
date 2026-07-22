import sys
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QLineEdit, QTextEdit

GLOBAL_TEXT = ""
GLOBAL_COUNTER = 0
GLOBAL_MODE = "default"

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PySide6 Code Smell Example")

        self.btn1 = QPushButton("Add Text")
        self.btn2 = QPushButton("Show Counter")
        self.btn3 = QPushButton("Reset")
        self.input1 = QLineEdit()
        self.label1 = QLabel("Status: Ready")
        self.textArea = QTextEdit()

        layout = QVBoxLayout()
        layout.addWidget(self.input1)
        layout.addWidget(self.btn1)
        layout.addWidget(self.btn2)
        layout.addWidget(self.btn3)
        layout.addWidget(self.label1)
        layout.addWidget(self.textArea)
        self.setLayout(layout)

        self.btn1.clicked.connect(self.handle_btn1)
        self.btn2.clicked.connect(self.handle_btn2)
        self.btn3.clicked.connect(self.handle_btn3)

    def handle_btn1(self):
        global GLOBAL_TEXT, GLOBAL_COUNTER
        text = self.input1.text()
        if len(text) > 0:
            GLOBAL_TEXT += text + " | "
            GLOBAL_COUNTER += 1
            self.textArea.append("Added: " + text)
        else:
            self.textArea.append("Empty input detected!")
        self.label1.setText("Status: Updated")

    def handle_btn2(self):
        global GLOBAL_COUNTER, GLOBAL_MODE
        if GLOBAL_COUNTER > 5:
            if GLOBAL_MODE == "default":
                self.textArea.append("Counter is large: " + str(GLOBAL_COUNTER))
            else:
                if GLOBAL_COUNTER % 2 == 0:
                    self.textArea.append("Even counter: " + str(GLOBAL_COUNTER))
                else:
                    self.textArea.append("Odd counter: " + str(GLOBAL_COUNTER))
        else:
            self.textArea.append("Counter small: " + str(GLOBAL_COUNTER))

    def handle_btn3(self):
        global GLOBAL_TEXT, GLOBAL_COUNTER, GLOBAL_MODE
        GLOBAL_TEXT = ""
        GLOBAL_COUNTER = 0
        GLOBAL_MODE = "reset"
        self.textArea.clear()
        self.label1.setText("Status: Reset Done")

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(400, 300)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()