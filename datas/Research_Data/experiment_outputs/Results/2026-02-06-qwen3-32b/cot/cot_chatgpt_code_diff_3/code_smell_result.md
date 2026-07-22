### Code Smell Type: Global State
**Problem Location:**  
`GLOBAL_THING = {...}` and all references to `GLOBAL_THING` in methods (`compute_title`, `handle_click`, `generate_text`, `do_periodic_stuff`).

**Detailed Explanation:**  
The code relies on a global dictionary to manage state, violating encapsulation principles. This creates hidden dependencies, making the code:
- Hard to test (state is shared and mutable across the entire application)
- Prone to unexpected side effects (e.g., `compute_title` alters `GLOBAL_THING["mood"]` without context)
- Unmaintainable (changes to global state require scanning all code for usage)
- Non-reusable (cannot be easily integrated into other contexts without global cleanup)

**Improvement Suggestions:**  
Replace global state with instance variables in `MyWindow`:
```python
class MyWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.clicks = 0
        self.mood = "idle"
        self.started = time.time()
        # ... rest of init
```
Remove `GLOBAL_THING` entirely and update all method logic to use instance attributes.

**Priority Level:** High  

---

### Code Smell Type: Blocking UI Thread
**Problem Location:**  
`handle_click` method: `time.sleep(0.1)`

**Detailed Explanation:**  
`time.sleep()` blocks the main event loop, freezing the UI for 100ms every 5 clicks. This causes:
- Poor user experience (UI becomes unresponsive)
- Unpredictable behavior (delays compound during rapid clicks)
- Violation of GUI best practices (all long-running operations must be offloaded)

**Improvement Suggestions:**  
Remove `time.sleep()` entirely. If a delay is necessary (e.g., for simulation), use `QTimer`:
```python
# Replace in handle_click:
if self.clicks % 5 == 0:
    QTimer.singleShot(100, self._simulate_delay)
    
def _simulate_delay(self):
    self.label.setText(self.generate_text())
```

**Priority Level:** High  

---

### Code Smell Type: Magic Numbers
**Problem Location:**  
Magic values `5`, `7`, `0.3`, `777` in `handle_click`, `do_periodic_stuff`, and `QTimer` initialization.

**Detailed Explanation:**  
Hard-coded values lack context, making code:
- Unreadable (no explanation of why `777` ms or `0.3` probability)
- Unmaintainable (changing values requires searching all occurrences)
- Error-prone (e.g., `777` may be a typo for `700`)

**Improvement Suggestions:**  
Define constants with descriptive names:
```python
# At module level
CLICKS_FOR_DELAY = 5
CLICKS_FOR_LABEL_UPDATE = 7
BUTTON_TEXT_CHANGE_PROBABILITY = 0.3
PERIODIC_INTERVAL_MS = 777

# In MyWindow.__init__:
self.timer.start(PERIODIC_INTERVAL_MS)
```

**Priority Level:** Medium  

---

### Code Smell Type: Misleading Function Name
**Problem Location:**  
`compute_title` method.

**Detailed Explanation:**  
The name implies a pure function (no side effects), but it **mutates global state** (`GLOBAL_THING["mood"]`). This violates:
- The principle of least surprise (readers expect no side effects)
- Code clarity (requires inspecting implementation to understand behavior)
- Maintainability (changes to mood logic become scattered)

**Improvement Suggestions:**  
Rename to reflect side effect or move mood management elsewhere:
```python
# Option 1: Rename with side effect
def update_mood_and_compute_title(self):
    self.mood = random.choice(["ok", "meh", "???"])
    return f"State: {self.mood}"

# Option 2: Decouple mood generation
def get_mood(self):
    return random.choice(["ok", "meh", "???"])

def compute_title(self):
    return f"State: {self.get_mood()}"
```

**Priority Level:** Medium  

---

### Code Smell Type: Tight Coupling
**Problem Location:**  
`MyWindow` class depends entirely on `GLOBAL_THING` instead of self-managing state.

**Detailed Explanation:**  
The class is tightly coupled to global state, causing:
- Dependency on external context (global state must exist)
- Difficulty in unit testing (requires global setup)
- Fragile code (changes to global state break unrelated logic)
- No clear ownership of state (who manages `started` vs `mood`?)

**Improvement Suggestions:**  
Fully encapsulate state within `MyWindow` (as shown in "Global State" fix). Ensure all state-related logic lives in the class.

**Priority Level:** High