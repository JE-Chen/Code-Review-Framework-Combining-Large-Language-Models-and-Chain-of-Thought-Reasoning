### 1. **No Global Assignment (`no-global-assign`)**
**Issue:**  
Assigning to a global variable like `globalLabel = None` and later modifying it inside a function using `global globalLabel` makes code unpredictable and hard to maintain.

**Root Cause:**  
Relying on shared mutable state across modules increases coupling and decreases testability.

**Impact:**  
Can cause race conditions, unintended side effects, and difficulties in unit testing or refactoring.

**Fix:**  
Replace global state with instance variables:
```python
class MyWindow:
    def __init__(self):
        self.global_label = None  # Instance variable
```

**Best Practice:**  
Avoid global variables; prefer encapsulation through classes or dependency injection.

---

### 2. **Unused Variable (`no-unused-vars`)**
**Issue:**  
The variable `anotherGlobal = "Hello"` is declared but never used.

**Root Cause:**  
Leftover or experimental code that was not cleaned up.

**Impact:**  
Confuses readers and clutters namespace.

**Fix:**  
Delete unused variables:
```python
# Remove this line entirely
# anotherGlobal = "Hello"
```

**Best Practice:**  
Keep code clean and remove dead code regularly.

---

### 3. **Function Too Long (`function-max-lines`)**
**Issue:**  
The function `veryStrangeFunctionNameThatDoesTooMuch` contains too many lines and responsibilities.

**Root Cause:**  
Violates the Single Responsibility Principle by combining multiple tasks.

**Impact:**  
Harder to read, debug, and modify. Increases chance of bugs.

**Fix:**  
Split into smaller functions:
```python
def create_widgets(self):
    ...

def setup_connections(self):
    ...

def configure_layout(self):
    ...
```

**Best Practice:**  
Each function should do one thing well.

---

### 4. **Inline Lambda for Event Connection (`no-inline-styles`)**
**Issue:**  
Using inline lambdas for connecting signals reduces readability.

**Root Cause:**  
Mixes logic with UI binding, making changes harder.

**Impact:**  
Makes debugging and testing more difficult.

**Fix:**  
Define named slots:
```python
def on_button_clicked(self):
    self.label.setText("Updated text")

self.btn1.clicked.connect(self.on_button_clicked)
```

**Best Practice:**  
Use descriptive method names and separate UI logic from actions.

---

### 5. **Nested Functions (`no-nested-functions`)**
**Issue:**  
A nested function `inner2` inside `inner` complicates code flow.

**Root Cause:**  
Poorly structured control flow or premature abstraction.

**Impact:**  
Reduced readability and increased difficulty in isolating behavior.

**Fix:**  
Move inner logic to top-level or class methods:
```python
def process_data(self):
    ...

def veryStrangeFunctionNameThatDoesTooMuch(self):
    self.process_data()
```

**Best Practice:**  
Minimize nesting and favor flat structures for clarity.

---

### 6. **Duplicate Event Handlers (`no-duplicate-event-handlers`)**
**Issue:**  
Multiple handlers connected to the same signal (`btn1.clicked`) may lead to unpredictable outcomes.

**Root Cause:**  
Accidental duplication during development or unclear ownership.

**Impact:**  
Unexpected behavior due to overwriting previous handlers.

**Fix:**  
Ensure only one handler per signal:
```python
self.btn1.clicked.connect(self.handle_click)
```

**Best Practice:**  
Explicitly manage event connections and avoid duplicates.

---

### 7. **Class Name Convention Violation (`class-name-convention`)**
**Issue:**  
Class name `MyWeirdWindow` doesn’t match standard naming conventions.

**Root Cause:**  
Inconsistent naming style across project.

**Impact:**  
Lowers professionalism and makes code harder to follow.

**Fix:**  
Rename to a clearer term:
```python
class MainWindow(QWidget):
```

**Best Practice:**  
Follow consistent naming patterns (PascalCase for classes).

---

### 8. **Function Name Convention Violation (`function-name-convention`)**
**Issue:**  
Function name `veryStrangeFunctionNameThatDoesTooMuch` lacks clarity.

**Root Cause:**  
Poor choice of descriptive verbs and nouns.

**Impact:**  
Confusing to other developers.

**Fix:**  
Rename with meaningful intent:
```python
def setup_user_interface(self):
    ...
```

**Best Practice:**  
Write self-documenting code by choosing good names.