### 1. Global State (no-global-state)  
**Issue**:  
Code uses a global dictionary (`GLOBAL_THING`) to manage state instead of encapsulating it within the class.  

**Plain English**:  
Global state creates hidden dependencies where any function can modify shared data, making the code fragile and hard to test.  

**Root Cause**:  
State is stored externally (global) rather than owned by the class that uses it. This violates encapsulation.  

**Impact**:  
- ❌ **Testability**: Tests require global setup/cleanup.  
- ❌ **Maintainability**: Scanning all code for state changes is error-prone.  
- ❌ **Side Effects**: `compute_title` alters global state unexpectedly.  
*Severity: High (breaks core design principles)*  

**Fix**:  
Replace global state with instance attributes.  
```python
# BEFORE
GLOBAL_THING = {"clicks": 0, "mood": "idle", ...}

class MyWindow(QWidget):
    def handle_click(self):
        GLOBAL_THING["clicks"] += 1  # Global mutation

# AFTER
class MyWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.clicks = 0
        self.mood = "idle"  # State owned by class
        self.started = time.time()

    def handle_click(self):
        self.clicks += 1  # Direct instance access
```

**Best Practice**:  
*Encapsulation (SOLID principle)* – State must be owned and managed by its logical owner.  

---

### 2. Blocking UI Thread (blocking-ui)  
**Issue**:  
`time.sleep(0.1)` freezes the UI in `handle_click()`.  

**Plain English**:  
Blocking the main thread with `sleep()` prevents the UI from rendering or responding to user input.  

**Root Cause**:  
Using synchronous delays in event handlers instead of asynchronous mechanisms.  

**Impact**:  
- ❌ **User Experience**: UI freezes for 100ms every 5 clicks.  
- ❌ **Unpredictability**: Rapid clicks compound delays.  
- ❌ **Anti-Pattern**: GUIs require non-blocking operations.  
*Severity: High (directly harms user experience)*  

**Fix**:  
Replace `sleep()` with `QTimer.singleShot()`.  
```python
# BEFORE
def handle_click(self):
    if self.clicks % 5 == 0:
        time.sleep(0.1)  # BLOCKING!

# AFTER
def handle_click(self):
    if self.clicks % 5 == 0:
        QTimer.singleShot(100, self._update_label)  # Non-blocking

def _update_label(self):
    self.label.setText(self.generate_text())
```

**Best Practice**:  
*Never block the main event loop in GUI code* – Use timers or worker threads for delays.  

---

### 3. Missing Class Docstring (missing-docs)  
**Issue**:  
`MyWindow` class lacks a docstring.  

**Plain English**:  
No documentation explains the class’s purpose or usage.  

**Root Cause**:  
Overlooking documentation as a non-functional requirement during development.  

**Impact**:  
- ❌ **Readability**: Developers must reverse-engineer the class.  
- ❌ **Onboarding**: New team members waste time understanding code.  
- ❌ **Maintenance**: Changes risk breaking undocumented behavior.  
*Severity: Medium (reduces long-term maintainability)*  

**Fix**:  
Add a concise class docstring.  
```python
# BEFORE
class MyWindow(QWidget):
    ...

# AFTER
class MyWindow(QWidget):
    """Custom window tracking click counts and mood.
    
    Updates label text periodically with randomized state.
    Uses non-blocking timers to avoid UI freezing.
    """
    ...
```

**Best Practice**:  
*Document public interfaces* – Follow PEP 257 for Python docstrings.  

---

### Summary of Fixes  
| Issue                  | Priority | Key Change                                  |
|------------------------|----------|---------------------------------------------|
| Global state           | High     | Replace `GLOBAL_THING` → `self.*`           |
| Blocking UI thread       | High     | Replace `time.sleep()` → `QTimer.singleShot()` |
| Missing docstring      | Medium   | Add class docstring                         |

**Critical Principle**:  
> **"Encapsulate state, never share it globally."**  
> Global state is a code smell – it breaks modularity and testability. Always own state within its logical owner (e.g., class instance).