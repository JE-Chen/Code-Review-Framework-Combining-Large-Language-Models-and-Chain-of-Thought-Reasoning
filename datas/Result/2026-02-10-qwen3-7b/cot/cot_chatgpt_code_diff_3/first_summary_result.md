# Code Review Summary

## Core Changes
- Implemented a GUI with click tracking, mood state, and periodic updates.
- Added random text generation and UI interactions.

## Impact Scope
- Affected `main.py` and `MyWindow` class.
- Core logic in `compute_title`, `generate_text`, and `do_periodic_stuff`.

## Purpose of Changes
- Improve user interaction and UI feedback.
- Maintain state and periodic updates.

## Risks and Considerations
- Potential issues with `GLOBAL_THING` state management.
- Missing tests for edge cases.

## Items to Confirm
- State consistency across `compute_title` and `generate_text`.
- Periodic updates and random text generation.
- Input validation for UI interactions.

---

## Code Diff Review

```diff
diff --git a/main.py b/main.py
--- a/main.py
+++ b/main.py
@@ -1,3 +1,11 @@
 import sys
 import random
 import time
+from PySide6.QtWidgets import (
+    QApplication, QWidget, QPushButton, QLabel, QVBoxLayout
+)
+from PySide6.QtCore import QTimer
+
+
+GLOBAL_THING = {
+    "clicks": 0,
+    "mood": "idle",
+    "started": time.time(),
+}
+
+
+class MyWindow(QWidget):
+    def __init__(self):
+        super().__init__()
+
+        self.label = QLabel("Hello but why")
+        self.button = QPushButton("Click maybe")
+        self.button.clicked.connect(self.handle_click)
+
+        layout = QVBoxLayout()
+        layout.addWidget(self.label)
+        layout.addWidget(self.button)
+        self.setLayout(layout)
+
+        self.resize(300, 200)
+        self.setWindowTitle(self.compute_title())
+
+        self.timer = QTimer(self)
+        self.timer.timeout.connect(self.do_periodic_stuff)
+        self.timer.start(777)
+
+
+    def compute_title(self):
+        GLOBAL_THING["mood"] = random.choice(["ok", "meh", "???"])
+        return f"State: {GLOBAL_THING['mood']}"
+
+
+    def handle_click(self):
+        GLOBAL_THING["clicks"] += 1
+
+        if GLOBAL_THING["clicks"] % 5 == 0:
+            time.sleep(0.1)
+
+        self.label.setText(self.generate_text())
+        self.setWindowTitle(self.compute_title())
+
+
+    def generate_text(self):
+        uptime = int(time.time() - GLOBAL_THING["started"])
+
+        if uptime % 2 == 0:
+            return f"Clicks: {GLOBAL_THING['clicks']}"
+        return f"Up for {uptime}s, mood={GLOBAL_THING['mood']}"
+
+
+    def do_periodic_stuff(self):
+        if random.random() < 0.3:
+            self.button.setText(
+                random.choice(["Click maybe", "Don't click", "Why click?"])
+            )
+
+        if GLOBAL_THING["clicks"] > 0 and GLOBAL_THING["clicks"] % 7 == 1:
+            self.label.setText("Something happened (probably)")
+
+
+def main():
+    app = QApplication(sys.argv)
+
+    GLOBAL_THING["mood"] = "starting"
+
+    win = MyWindow()
+    win.show()
+
+    result = app.exec()
+    sys.exit(result if result is not None else 0)
+
+
+if __name__ == "__main__":
+    main()
```

---

## Key Feedback

1. **Readability**:
   - Use 4-space indentation.
   - Add space after comments.

2. **Naming**:
   - `GLOBAL_THING` → `APP_STATE` for clarity.
   - `generate_text` → `get_text()` for better semantic clarity.

3. **Consistency**:
   - Use `self.` for class attributes.
   - Maintain `random.choice` pattern.

4. **Logic**:
   - `uptime % 2 == 0` → `uptime % 2 == 0` is correct.
   - Add `if GLOBAL_THING["clicks"] == 0` check in `handle_click`.

5. **Testing**:
   - Add unit tests for edge cases.
   - Add docstrings for functions.

6. **Performance**:
   - `time.sleep(0.1)` is unnecessary if clicks are not 0.

7. **Security**:
   - No input validation for `GLOBAL_THING` state.