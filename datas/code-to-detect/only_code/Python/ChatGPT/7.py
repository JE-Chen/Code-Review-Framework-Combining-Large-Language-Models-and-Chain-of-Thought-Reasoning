# 一個「功能正常」的 PySide6 GUI 程式
# 但寫法是教科書級 GUI Code Smell 展覽會 🤮

import sys
import time
from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel,
    QLineEdit, QTextEdit, QVBoxLayout, QHBoxLayout
)
from PySide6.QtCore import QTimer


# ❌ 全域 QApplication 依賴（Hidden Global Dependency）
app = QApplication(sys.argv)


# ❌ God Widget：一個視窗包辦 UI + 邏輯 + 狀態 + 商業規則
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        # ❌ Magic Geometry Numbers：全部硬編碼位置與大小
        self.setWindowTitle("User Manager")
        self.setGeometry(100, 100, 500, 400)

        # ❌ UI 元件直接當成資料模型（UI as Data Model）
        self.users = []   # list of dict，混在 GUI 類別裡

        # ❌ 控制項命名極度不一致（Inconsistent Naming Convention）
        self.nameInput = QLineEdit()
        self.txtAge = QLineEdit()
        self.btn_add_user = QPushButton("Add User")
        self.buttonDelete = QPushButton("Delete Last")
        self.lblStatus = QLabel("Ready")
        self.output = QTextEdit()

        # ❌ 硬編碼樣式（Hard-coded Style）
        self.lblStatus.setStyleSheet("color: blue; font-size: 14px;")

        # ❌ 手動組 layout，重複程式碼（Duplicated Layout Code）
        top_layout = QHBoxLayout()
        top_layout.addWidget(QLabel("Name:"))
        top_layout.addWidget(self.nameInput)

        mid_layout = QHBoxLayout()
        mid_layout.addWidget(QLabel("Age:"))
        mid_layout.addWidget(self.txtAge)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.btn_add_user)
        btn_layout.addWidget(self.buttonDelete)

        main_layout = QVBoxLayout()
        main_layout.addLayout(top_layout)
        main_layout.addLayout(mid_layout)
        main_layout.addLayout(btn_layout)
        main_layout.addWidget(self.output)
        main_layout.addWidget(self.lblStatus)

        self.setLayout(main_layout)

        # ❌ 訊號直接接 lambda，邏輯塞在 UI 層（Inline Slot Logic）
        self.btn_add_user.clicked.connect(lambda: self.add_user())
        self.buttonDelete.clicked.connect(lambda: self.delete_user())

        # ❌ 濫用 Timer 當背景輪詢（Polling Smell）
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_status)
        self.timer.start(1000)   # 每秒刷新一次，毫無必要

        # ❌ 動態新增屬性（Dynamic Attribute Abuse）
        self.last_action = None


    # ❌ Slot 函式過度肥大（Fat Slot）
    def add_user(self):
        name = self.nameInput.text()
        age_text = self.txtAge.text()

        # ❌ 驗證邏輯寫在 UI 事件中（Validation in View）
        if name == "" or age_text == "":
            self.lblStatus.setText("Missing input")
            return

        try:
            age = int(age_text)
        except:
            # ❌ Overly Broad Exception Catch
            self.lblStatus.setText("Invalid age")
            return

        # ❌ 商業規則直接寫在 UI 裡（Business Logic in GUI）
        if age < 0:
            self.lblStatus.setText("Age cannot be negative")
            return

        user = {"name": name, "age": age}
        self.users.append(user)

        # ❌ Blocking UI Thread：直接 sleep 卡住整個視窗
        time.sleep(0.3)

        # ❌ 重複渲染邏輯（Duplicated Rendering Logic）
        self.output.append(f"Added: {name}, {age}")

        # ❌ 狀態旗標濫用（Flag State Smell）
        self.last_action = "add"

        # ❌ UI 狀態同步靠手動管理（Manual State Synchronization）
        self.lblStatus.setText(f"Total users: {len(self.users)}")


    # ❌ 幾乎複製貼上的 Slot（Copy–Paste Programming）
    def delete_user(self):
        if len(self.users) == 0:
            self.lblStatus.setText("No users to delete")
            return

        user = self.users.pop()

        # ❌ 重複邏輯 again
        time.sleep(0.2)

        self.output.append(f"Deleted: {user['name']}")

        self.last_action = "delete"
        self.lblStatus.setText(f"Total users: {len(self.users)}")


    # ❌ 定時輪詢 UI 狀態（Polling Instead of Events）
    def refresh_status(self):
        # ❌ 依賴 last_action 的隱藏狀態（Hidden State Dependency）
        if self.last_action == "add":
            self.lblStatus.setStyleSheet("color: green;")
        elif self.last_action == "delete":
            self.lblStatus.setStyleSheet("color: red;")
        else:
            self.lblStatus.setStyleSheet("color: blue;")


# ❌ Main function 幾乎沒抽象，直接操作 UI 類別
def main():
    # ❌ 重複建立視窗風格（Hard-coded Window Setup）
    window = MainWindow()
    window.show()

    # ❌ 在 GUI 程式中直接用 sys.exit（Tight Coupling to System）
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
