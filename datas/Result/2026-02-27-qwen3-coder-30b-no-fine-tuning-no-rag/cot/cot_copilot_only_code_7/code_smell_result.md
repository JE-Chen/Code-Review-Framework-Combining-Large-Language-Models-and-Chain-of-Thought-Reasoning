## Code Review: PySide6 GUI Application

### Code Smell Type: Global State Usage
**Problem Location:** Lines 5-7, `handle_btn1`, `handle_btn2`, `handle_btn3` functions

**Detailed Explanation:**
The code uses three global variables (`GLOBAL_TEXT`, `GLOBAL_COUNTER`, `GLOBAL_MODE`) to store application state. This creates tight coupling between functions and makes the code difficult to reason about, debug, and test. Global state introduces side effects, makes unit testing impossible without complex setup, and violates the principle of encapsulation.

**Improvement Suggestions:**
Replace global variables with instance attributes in the `MainWindow` class:
```python
def __init__(self):
    super().__init__()
    # ... existing initialization ...
    self.text_content = ""
    self.counter = 0
    self.mode = "default"

def handle_btn1(self):
    text = self.input1.text()
    if len(text) > 0:
        self.text_content += text + " | "
        self.counter += 1
        self.textArea.append("Added: " + text)
    else:
        self.textArea.append("Empty input detected!")
    self.label1.setText("Status: Updated")
```

**Priority Level:** High

---

### Code Smell Type: Magic Strings
**Problem Location:** Line 19, "default" string literal in `handle_btn2`

**Detailed Explanation:**
The string "default" appears as a magic string in the conditional logic. This makes the code less maintainable since changing the mode name requires searching through the entire codebase. It also reduces readability by hiding the semantic meaning of the value.

**Improvement Suggestions:**
Define constants for mode values:
```python
DEFAULT_MODE = "default"
EVEN_MODE = "even"
ODD_MODE = "odd"
# Replace "default" with DEFAULT_MODE throughout the code
```

**Priority Level:** Medium

---

### Code Smell Type: Long Function
**Problem Location:** `handle_btn2` method (lines 30-41)

**Detailed Explanation:**
The `handle_btn2` function performs multiple responsibilities: checking counter thresholds, determining mode behavior, and handling different counter parity cases. This violates the Single Responsibility Principle and makes the function hard to read, test, and modify. The nested conditionals make the logic flow confusing.

**Improvement Suggestions:**
Break down the function into smaller, focused methods:
```python
def _check_counter_threshold(self):
    return self.counter > 5

def _format_large_counter_message(self):
    if self.mode == "default":
        return f"Counter is large: {self.counter}"
    elif self.counter % 2 == 0:
        return f"Even counter: {self.counter}"
    else:
        return f"Odd counter: {self.counter}"

def _format_small_counter_message(self):
    return f"Counter small: {self.counter}"

def handle_btn2(self):
    if self._check_counter_threshold():
        message = self._format_large_counter_message()
    else:
        message = self._format_small_counter_message()
    self.textArea.append(message)
```

**Priority Level:** High

---

### Code Smell Type: Inconsistent Naming
**Problem Location:** Variable names `btn1`, `btn2`, `btn3` (lines 12-14)

**Detailed Explanation:**
The button variable names (`btn1`, `btn2`, `btn3`) are non-descriptive and don't convey their purpose. This makes the code harder to understand for new developers and reduces maintainability. A more descriptive naming convention would improve readability.

**Improvement Suggestions:**
Use descriptive names like `add_text_button`, `show_counter_button`, `reset_button`:
```python
self.add_text_button = QPushButton("Add Text")
self.show_counter_button = QPushButton("Show Counter")
self.reset_button = QPushButton("Reset")
```

**Priority Level:** Medium

---

### Code Smell Type: Magic Numbers
**Problem Location:** Line 33, threshold value `5`

**Detailed Explanation:**
The number `5` used as a counter threshold is a magic number. It's unclear what significance this number has without looking at the context. This reduces code readability and makes future modifications harder when the threshold needs to be changed.

**Improvement Suggestions:**
Define a named constant for the threshold:
```python
COUNTER_THRESHOLD = 5
# Replace 5 with COUNTER_THRESHOLD
```

**Priority Level:** Medium

---

### Code Smell Type: Duplicated Logic
**Problem Location:** Multiple places where counter values are converted to strings

**Detailed Explanation:**
The pattern of converting counter values to strings and appending them to the text area occurs multiple times. While not critical, this repetition suggests opportunities for abstraction or helper methods to reduce redundancy.

**Improvement Suggestions:**
Create a helper method for consistent string formatting:
```python
def _format_counter_message(self, prefix, counter_value):
    return f"{prefix}: {counter_value}"

# Use this in handle_btn2 instead of repeated string concatenations
```

**Priority Level:** Low

---

### Code Smell Type: Tight Coupling
**Problem Location:** All handler methods rely on global state and shared dependencies

**Detailed Explanation:**
The three handler methods (`handle_btn1`, `handle_btn2`, `handle_btn3`) are tightly coupled to global variables rather than to the object's internal state. This prevents reuse of these methods in other contexts and makes testing particularly difficult since you need to set up global state before testing.

**Improvement Suggestions:**
Move all state management into the class instance variables and remove reliance on global scope entirely. Each handler should only interact with its own instance data.

**Priority Level:** High

---

### Code Smell Type: Poor Error Handling
**Problem Location:** Input validation in `handle_btn1`

**Detailed Explanation:**
While basic validation exists (checking for empty input), there's no handling for edge cases like very long inputs or special characters. The code assumes all inputs will be valid, which could lead to unexpected behavior or crashes in production scenarios.

**Improvement Suggestions:**
Add more robust input validation:
```python
def handle_btn1(self):
    text = self.input1.text().strip()  # Strip whitespace
    if len(text) == 0:
        self.textArea.append("Empty input detected!")
        return
    
    if len(text) > 1000:  # Add reasonable length limit
        self.textArea.append("Input too long!")
        return
        
    # Continue with current logic...
```

**Priority Level:** Medium