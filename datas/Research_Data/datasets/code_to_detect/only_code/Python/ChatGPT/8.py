import sys
import time
from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel,
    QLineEdit, QTextEdit, QVBoxLayout, QHBoxLayout
)
from PySide6.QtCore import QTimer


app = QApplication(sys.argv)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("User Manager")
        self.setGeometry(100, 100, 500, 400)

        self.users = []

        self.nameInput = QLineEdit()
        self.txtAge = QLineEdit()
        self.btn_add_user = QPushButton("Add User")
        self.buttonDelete = QPushButton("Delete Last")
        self.lblStatus = QLabel("Ready")
        self.output = QTextEdit()

        self.lblStatus.setStyleSheet("color: blue; font-size: 14px;")

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

        self.btn_add_user.clicked.connect(lambda: self.add_user())
        self.buttonDelete.clicked.connect(lambda: self.delete_user())

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_status)
        self.timer.start(1000)

        self.last_action = None


    def add_user(self):
        name = self.nameInput.text()
        age_text = self.txtAge.text()

        if name == "" or age_text == "":
            self.lblStatus.setText("Missing input")
            return

        try:
            age = int(age_text)
        except:
            self.lblStatus.setText("Invalid age")
            return

        if age < 0:
            self.lblStatus.setText("Age cannot be negative")
            return

        user = {"name": name, "age": age}
        self.users.append(user)

        time.sleep(0.3)

        self.output.append(f"Added: {name}, {age}")

        self.last_action = "add"

        self.lblStatus.setText(f"Total users: {len(self.users)}")


    def delete_user(self):
        if len(self.users) == 0:
            self.lblStatus.setText("No users to delete")
            return

        user = self.users.pop()

        time.sleep(0.2)

        self.output.append(f"Deleted: {user['name']}")

        self.last_action = "delete"
        self.lblStatus.setText(f"Total users: {len(self.users)}")


    def refresh_status(self):
        if self.last_action == "add":
            self.lblStatus.setStyleSheet("color: green;")
        elif self.last_action == "delete":
            self.lblStatus.setStyleSheet("color: red;")
        else:
            self.lblStatus.setStyleSheet("color: blue;")


def main():
    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
