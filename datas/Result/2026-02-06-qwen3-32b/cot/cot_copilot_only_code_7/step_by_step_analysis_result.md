### Code Quality Review Report

---

#### **1. Global Variables Used for Application State**  
**Issue Summary**  
Global variables (`GLOBAL_TEXT`, `GLOBAL_COUNTER`, `GLOBAL_MODE`) are used to manage application state, violating encapsulation and making the code difficult to test.  

**Root Cause**  
The code relies on global state instead of object-oriented state management. This stems from a procedural programming mindset where state is shared globally rather than encapsulated within class instances.  

**Impact**  
- **Testability**: Impossible to isolate methods for unit testing (e.g., `handle_btn1` depends on external state).  
- **Maintainability**: Hidden dependencies cause bugs (e.g., accidental state changes from unrelated code).  
- **Scalability**: Global state becomes a bottleneck in larger applications.  
*Severity: High (blocks core development practices like testing and refactoring).*  

**Suggested Fix**  
Replace global variables with instance attributes:  
```python
# BEFORE
GLOBAL_TEXT = ""
GLOBAL_COUNTER = 0

class MainWindow(QWidget):
    def handle_btn1(self):
        global GLOBAL_TEXT, GLOBAL_COUNTER
        GLOBAL_TEXT += "input | "
        GLOBAL_COUNTER += 1

# AFTER
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.text = ""       # Instance attribute instead of global
        self.counter = 0     # Instance attribute instead of global

    def handle_btn1(self):
        self.text += "input | "  # Directly use self.text
        self.counter += 1
```

**Best Practice**  
Adhere to **Single Responsibility Principle (SRP)**: Encapsulate state within the class that owns it. Avoid global state entirely—use dependency injection for cross-component state sharing.

---

#### **2. Missing Class Docstring**  
**Issue Summary**  
The `MainWindow` class lacks a docstring explaining its purpose and behavior.  

**Root Cause**  
Documentation was omitted during implementation, treating code as self-explanatory. This is a common oversight in feature-focused development.  

**Impact**  
- **Onboarding**: New developers waste time deciphering the class's role.  
- **Maintainability**: Critical context (e.g., "This class manages the text counter UI") is missing.  
- **Professionalism**: Production code without documentation signals low quality.  
*Severity: Medium (impedes collaboration and long-term maintenance).*  

**Suggested Fix**  
Add a concise docstring:  
```python
class MainWindow(QWidget):
    """Main application window for text counter demo. 
    Manages UI state and handles user interactions for text history and counter."""
    
    def __init__(self):
        """Initialize UI components and state."""
        super().__init__()
        # ... rest of init unchanged
```

**Best Practice**  
Follow **PEP 257**: Every public class and method must have a docstring describing purpose, inputs, outputs, and side effects. Prioritize clarity over completeness.

---

#### **3. Missing Method Docstring**  
**Issue Summary**  
The `handle_btn1` method lacks a docstring detailing its behavior.  

**Root Cause**  
Developers often skip method-level documentation after adding class-level docstrings, assuming method logic is obvious.  

**Impact**  
- **Debugging**: Unclear what `handle_btn1` does (e.g., "Why does it append ` | `?").  
- **Testing**: Test cases cannot be written confidently without understanding side effects.  
- **Refactoring**: Risk of breaking unintended behavior when modifying the method.  
*Severity: Medium (reduces code reliability without immediate failure).*  

**Suggested Fix**  
Document method behavior and side effects:  
```python
def handle_btn1(self):
    """Append user input to history and increment counter.
    
    Side effects: 
    - Updates self.text (appends input + ' | ')
    - Increments self.counter
    """
    self.text += "input | "
    self.counter += 1
```

**Best Practice**  
Document **all** public methods: Describe inputs, outputs, and side effects. Use the [Google Style](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings) for consistency.

---

### Summary of Fixes & Priority  
| Issue                          | Priority | Impact |  
|--------------------------------|----------|--------|  
| Global variables               | High     | Blocks testing/refactoring |  
| Missing class docstring        | Medium   | Hinders onboarding |  
| Missing method docstring       | Medium   | Increases bug risk |  

**Critical Next Steps**  
1. Replace all global variables with instance attributes.  
2. Add docstrings to *every* public class and method.  
3. Refactor nested conditionals (e.g., in `handle_btn2`) for clarity.  

> 💡 **Prevention Principle**: *"Document everything you’d explain to a colleague."* This reduces cognitive load for all developers and aligns with professional coding standards.