### Code Smell Type: Overly Long and Uninformative Function Name  
**Problem Location**:  
```python
def veryStrangeFunctionNameThatDoesTooMuch(window):
```

**Detailed Explanation**:  
The function name violates naming conventions by being excessively long and non-descriptive. It fails to convey the function's purpose (setup GUI elements) while hinting at excessive responsibilities ("TooMuch"). This hinders readability and maintainability, making it difficult for developers to understand the function's role without reading its body. It also signals a deeper issue: the function does multiple unrelated tasks (layout setup, widget creation, event handling), violating the Single Responsibility Principle.

**Improvement Suggestions**:  
Rename to a concise, descriptive name like `setup_main_interface` or `initialize_user_interface`. Split the function's responsibilities into focused methods (e.g., `create_layout()`, `connect_buttons()`). Move setup logic into the `MyWeirdWindow` class to eliminate global dependencies.

**Priority Level**: Medium  

---

### Code Smell Type: Global Variables  
**Problem Location**:  
```python
globalLabel = None
anotherGlobal = "Hello"
```

**Detailed Explanation**:  
Unnecessary global variables (`globalLabel`, `anotherGlobal`) create tight coupling, obscure data flow, and complicate testing. `globalLabel` is mutated within a function using `global`, breaking encapsulation. `anotherGlobal` is unused, introducing dead code. Globals make code fragile: changes to global state can cause unexpected side effects across unrelated components.

**Improvement Suggestions**:  
1. Remove `globalLabel` and `anotherGlobal`.  
2. Store UI elements as class attributes in `MyWeirdWindow`:  
   ```python
   class MyWeirdWindow(QWidget):
       def __init__(self):
           super().__init__()
           self.label = QLabel("這是一個奇怪的 GUI")
   ```
3. Replace `veryStrangeFunctionNameThatDoesTooMuch` with a method that uses `self.label` directly.

**Priority Level**: High  

---

### Code Smell Type: Redundant Signal Connections  
**Problem Location**:  
```python
btn1.clicked.connect(lambda: lbl.setText("你按了第一個按鈕"))
btn1.clicked.connect(lambda: lbl.setText("真的按了第一個按鈕"))
btn2.clicked.connect(lambda: lbl.setText("你按了第二個按鈕"))
btn2.clicked.connect(inner)  # inner() also sets lbl
```

**Detailed Explanation**:  
Each button has duplicate connections that overwrite label text. For `btn1`, the second connection overrides the first. For `btn2`, the direct connection and `inner()` both update the label. This creates confusing behavior and bugs (e.g., "真的按了第一個按鈕" never appears). Redundant connections also increase maintenance overhead.

**Improvement Suggestions**:  
Remove duplicate connections. Use a single handler per button:  
```python
btn1.clicked.connect(lambda: lbl.setText("你按了第一個按鈕"))
btn2.clicked.connect(lambda: lbl.setText("你按了第二個按鈕"))
# Remove the inner function entirely
```

**Priority Level**: Medium  

---

### Code Smell Type: Function Violating Single Responsibility Principle  
**Problem Location**:  
Full function definition of `veryStrangeFunctionNameThatDoesTooMuch(window)`.

**Detailed Explanation**:  
This function handles layout creation, widget initialization, event binding, and nested logic. It violates SRP by combining unrelated responsibilities. This makes the function:
- Hard to test (requires full UI context)
- Prone to bugs (e.g., redundant connections)
- Impossible to reuse or modify independently.

**Improvement Suggestions**:  
Refactor into cohesive methods:  
```python
def setup_layout(window):
    layout = QVBoxLayout()
    # ... create widgets and add to layout
    return layout

def connect_buttons(lbl, btn1, btn2):
    btn1.clicked.connect(lambda: lbl.setText("你按了第一個按鈕"))
    btn2.clicked.connect(lambda: lbl.setText("你按了第二個按鈕"))
```
Move setup into `MyWeirdWindow.__init__` to use class attributes.

**Priority Level**: High  

---

### Code Smell Type: Unused Variable  
**Problem Location**:  
```python
anotherGlobal = "Hello"
```

**Detailed Explanation**:  
The variable `anotherGlobal` is defined but never used. Dead code clutters the codebase, distracts readers, and increases cognitive load. It may indicate incomplete refactoring or accidental copy-paste.

**Improvement Suggestions**:  
Delete the unused variable. If it was intended for future use, add a comment explaining its purpose.

**Priority Level**: Low  

---

### Code Smell Type: Unnecessary Nested Functions  
**Problem Location**:  
```python
def inner():
    def inner2():
        lbl.setText("巢狀函式被呼叫")
    inner2()
btn2.clicked.connect(inner)
```

**Detailed Explanation**:  
The nested `inner()` and `inner2()` functions add no value over a simple lambda. They complicate control flow and obscure the intent (label update). This is a symptom of the function doing too much (violating SRP).

**Improvement Suggestions**:  
Replace with a direct lambda:  
```python
btn2.clicked.connect(lambda: lbl.setText("巢狀函式被呼叫"))
```
*Note: This connection should be removed per the "Redundant Signal Connections" fix.*

**Priority Level**: Low