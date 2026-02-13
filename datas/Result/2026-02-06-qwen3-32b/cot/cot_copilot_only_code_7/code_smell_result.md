### Code Smell Type: Use of Global Variables
**Problem Location:**
```python
GLOBAL_TEXT = ""
GLOBAL_COUNTER = 0
GLOBAL_MODE = "default"

class MainWindow(QWidget):
    # ... (methods using global variables)
    def handle_btn1(self):
        global GLOBAL_TEXT, GLOBAL_COUNTER
        # ...
    def handle_btn2(self):
        global GLOBAL_COUNTER, GLOBAL_MODE
        # ...
    def handle_btn3(self):
        global GLOBAL_TEXT, GLOBAL_COUNTER, GLOBAL_MODE
        # ...
```

**Detailed Explanation:**  
Global variables violate encapsulation and create hidden dependencies. Here, `GLOBAL_TEXT`, `GLOBAL_COUNTER`, and `GLOBAL_MODE` are shared across the entire program, making the code:
- Hard to reason about (e.g., unexpected state changes from anywhere)
- Impossible to test in isolation (requires resetting global state between tests)
- Prone to race conditions in concurrent environments
- Violates the Single Responsibility Principle (SRP) by coupling UI logic with state management

**Improvement Suggestions:**  
Replace global variables with instance attributes:
```python
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.text_store = ""  # Instead of GLOBAL_TEXT
        self.counter = 0      # Instead of GLOBAL_COUNTER
        self.mode = "default" # Instead of GLOBAL_MODE
        # ... rest of init unchanged
```
Then update all method references to use `self.text_store`, `self.counter`, etc. This centralizes state within the class, improves testability, and eliminates hidden dependencies.

**Priority Level:** High

---

### Code Smell Type: Complex Conditional Logic
**Problem Location:**
```python
def handle_btn2(self):
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
```

**Detailed Explanation:**  
Deeply nested conditionals reduce readability and increase bug risk. The logic:
- Mixes threshold checks (`>5`) with mode-specific behavior
- Has duplicated string construction
- Makes future modifications error-prone (e.g., adding new modes requires editing the same block)
- Violates SRP by handling multiple concerns in one method

**Improvement Suggestions:**  
Refactor into separate helper methods:
```python
def handle_btn2(self):
    if self.counter <= 5:
        self._append_counter_small()
    elif self.mode == "default":
        self._append_counter_large()
    else:
        self._append_counter_even_odd()

def _append_counter_small(self):
    self.textArea.append(f"Counter small: {self.counter}")

def _append_counter_large(self):
    self.textArea.append(f"Counter is large: {self.counter}")

def _append_counter_even_odd(self):
    self.textArea.append(f"{'Even' if self.counter % 2 == 0 else 'Odd'} counter: {self.counter}")
```
*Benefits:* Clearer intent, easier to extend (add new modes), and testable components.

**Priority Level:** Medium

---

### Code Smell Type: Unused Global Variable
**Problem Location:**
```python
GLOBAL_MODE = "default"
# ... in handle_btn3:
GLOBAL_MODE = "reset"  # Never used elsewhere
```

**Detailed Explanation:**  
`GLOBAL_MODE` is set to `"reset"` in `handle_btn3` but never consumed. This:
- Creates confusion about its purpose
- Wastes developer time debugging non-existent behavior
- Introduces dead code that increases cognitive load
- Contradicts the global variable smell (if it existed for a purpose, it should be used consistently)

**Improvement Suggestions:**  
Remove `GLOBAL_MODE` entirely. If mode-based behavior is needed, implement it via `self.mode` (as fixed in the first smell). If the mode is only used for the reset status, replace with:
```python
self.label1.setText("Status: Reset Done")  # Instead of setting GLOBAL_MODE
```

**Priority Level:** Medium

---

### Code Smell Type: Missing Documentation
**Problem Location:**  
All class and method definitions lack docstrings.

**Detailed Explanation:**  
Absence of documentation:
- Hinders new developers understanding the code
- Makes it impossible to auto-generate API docs
- Reduces maintainability (e.g., why does `handle_btn1` append `" | "`?)
- Violates professional standards for production code

**Improvement Suggestions:**  
Add concise docstrings:
```python
class MainWindow(QWidget):
    """Main application window for text counter demo."""
    
    def __init__(self):
        """Initialize UI components and state."""
        super().__init__()
        # ... (rest unchanged)

    def handle_btn1(self):
        """Append input text to history and increment counter."""
        # ... (rest unchanged)
```

**Priority Level:** Medium

---

### Code Smell Type: Inefficient String Concatenation
**Problem Location:**
```python
GLOBAL_TEXT += text + " | "
```

**Detailed Explanation:**  
String concatenation with `+=` in a loop (even if infrequent) creates O(n²) performance in Python due to repeated memory allocation. While negligible here, it establishes bad habits for larger applications.

**Improvement Suggestions:**  
Use a list to accumulate parts and join at the end:
```python
# Replace GLOBAL_TEXT with self.text_store (as fixed in first smell)
self.text_store_parts.append(text)
self.textArea.append(f"Added: {text}")
# Later, when displaying: " | ".join(self.text_store_parts)
```
*Note:* This is low-priority since the current usage is small-scale, but recommended for consistency.

**Priority Level:** Low