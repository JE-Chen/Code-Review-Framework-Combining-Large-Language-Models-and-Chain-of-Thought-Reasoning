### PR Summary Template

#### Summary Rules
- **Key changes**: Implemented a simple user management application using PySide6.
- **Impact scope**: Affects `MainWindow` class and related UI components.
- **Purpose of changes**: To create a GUI tool for adding and deleting users, displaying their details, and updating status messages.
- **Risks and considerations**: Potential issues with input validation and threading due to `time.sleep`.
- **Items to confirm**:
  - Ensure all error messages are clear and consistent.
  - Confirm the use of `time.sleep` is appropriate and does not affect responsiveness.
  - Validate the logic for adding and deleting users.

#### Code diff to review
```python
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

        time.sleep(0.3)  # This can block the UI thread

        self.output.append(f"Added: {name}, {age}")

        self.last_action = "add"

        self.lblStatus.setText(f"Total users: {len(self.users)}")


    def delete_user(self):
        if len(self.users) == 0:
            self.lblStatus.setText("No users to delete")
            return

        user = self.users.pop()

        time.sleep(0.2)  # This can block the UI thread

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
```

### Detailed Code Review

1. **Readability & Consistency**
   - **Indentation**: Proper indentation is used.
   - **Formatting**: Consistent spacing around operators and after commas.
   - **Comments**: Comments are missing.

2. **Naming Conventions**
   - **Variable Names**: Descriptive (`users`, `nameInput`, `txtAge`, etc.).
   - **Function Names**: Descriptive (`add_user`, `delete_user`, etc.).
   - **Class Name**: `MainWindow` is descriptive.

3. **Software Engineering Standards**
   - **Modularity**: The code is modular, with each method having a single responsibility.
   - **Maintainability**: The structure is clear, but could benefit from breaking down larger methods into smaller ones.
   - **Testability**: No unit tests are provided.

4. **Logic & Correctness**
   - **Boundary Conditions**: Input validation checks for empty strings and invalid ages.
   - **Exception Handling**: Basic exception handling for type conversion.
   - **Edge Cases**: Handles cases where no users exist for deletion.

5. **Performance & Security**
   - **Unnecessary Blocking**: `time.sleep` blocks the UI thread, which is inefficient.
   - **Resource Management**: No explicit resource management required.

6. **Documentation & Testing**
   - **Comments**: Missing docstrings and inline comments explaining complex logic.
   - **Tests**: No unit tests or integration tests.

### Recommendations
- **Refactor `time.sleep`**: Use asynchronous operations or timers to avoid blocking the UI.
- **Add Unit Tests**: Write tests for edge cases and functionality.
- **Docstrings**: Add docstrings for classes and methods.
- **Consistent Styling**: Apply a consistent code formatter like Black.