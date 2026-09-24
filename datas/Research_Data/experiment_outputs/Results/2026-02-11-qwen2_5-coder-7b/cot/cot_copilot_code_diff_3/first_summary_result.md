## PR Summary Template

### Key Changes
- Added a new Python script `gui.py` implementing a GUI application using PySide6.

### Impact Scope
- Affects the `gui.py` module and its associated classes/functions.

### Purpose of Changes
- To create a simple GUI application demonstrating various UI components and interactions.

### Risks and Considerations
- The use of global variables (`globalLabel`, `anotherGlobal`) may lead to unexpected behavior if not managed carefully.
- The function `veryStrangeFunctionNameThatDoesTooMuch` is overly complex and difficult to understand.
- Potential issues with nested functions and lambda expressions could affect performance or readability.

### Items to Confirm
- Ensure that the GUI behaves as expected when buttons are clicked.
- Validate that there are no unintended side effects due to global variable usage.
- Review the complexity of the `veryStrangeFunctionNameThatDoesTooMuch` function for readability improvements.

---

## Code Diff to Review
```python
diff --git a/gui.py b/gui.py
new file mode 100644
index 0000000..1111111
--- /dev/null
+++ b/gui.py
@@
+import sys
+from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout
+
+globalLabel = None
+anotherGlobal = "Hello"
+
+def veryStrangeFunctionNameThatDoesTooMuch(window):
+    global globalLabel
+    layout = QVBoxLayout()
+    btn1 = QPushButton("按我一下")
+    btn2 = QPushButton("再按我一下")
+    lbl = QLabel("這是一個奇怪的 GUI")
+    globalLabel = lbl
+
+    btn1.clicked.connect(lambda: lbl.setText("你按了第一個按鈕"))
+    btn1.clicked.connect(lambda: lbl.setText("真的按了第一個按鈕"))
+    btn2.clicked.connect(lambda: lbl.setText("你按了第二個按鈕"))
+
+    def inner():
+        def inner2():
+            lbl.setText("巢狀函式被呼叫")
+        inner2()
+    btn2.clicked.connect(inner)
+
+    layout.addWidget(lbl)
+    layout.addWidget(btn1)
+    layout.addWidget(btn2)
+    window.setLayout(layout)
+
+class MyWeirdWindow(QWidget):
+    def __init__(self):
+        super().__init__()
+        self.setWindowTitle("臭味 GUI")
+        veryStrangeFunctionNameThatDoesTooMuch(self)
+
+if __name__ == "__main__":
+    app = QApplication(sys.argv)
+    w = MyWeirdWindow()
+    w.show()
+    sys.exit(app.exec())
```

This code introduces a new GUI application using PySide6. It includes a main window with two buttons and a label. The button click events update the label's text. There are also nested functions within `veryStrangeFunctionNameThatDoesTooMuch`. 

Reviewers should ensure the GUI works correctly and consider refactoring the complex function for better readability and maintainability.