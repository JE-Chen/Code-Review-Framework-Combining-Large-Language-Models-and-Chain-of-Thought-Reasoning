### **Code Smell Analysis & Recommendations**

---

### **1. Tight Coupling**  
**Issue**: `GLOBAL_STATE` is used directly in all functions.  
**Impact**: Hard to isolate or test; propagation of changes affects all components.  
**Fix**: Encapsulate state in a class or module.  
**Example**:  
```python
class AppState:
    def __init__(self):
        self.state = {}

    def reset_state(self):
        self.state = {}
```
**Best Practice**: Encapsulate shared state in a class to improve modularity.

---

### **2. Magic Numbers**  
**Issue**: Constants like `77` are hardcoded.  
**Impact**: Values lack context and are hard to maintain.  
**Fix**: Replace with named constants.  
**Example**:  
```python
THRESHOLD = 77
INITIAL_DATA_RANGE = (1, 21)
```
**Best Practice**: Use constants for shared values.

---

### **3. Long Function**  
**Issue**: `process_items()` contains complex logic.  
**Impact**: Difficult to read and test.  
**Fix**: Split into smaller helper functions.  
**Example**:  
```python
def process_even_odd(data):
    return [x for x in data if x % 2 == 0]

def process_threshold(data):
    return [x for x in data if x > THRESHOLD]
```
**Best Practice**: Follow the Single Responsibility Principle.

---

### **4. Unclear Naming**  
**Issue**: `GLOBAL_STATE` is vague.  
**Impact**: Reduces clarity and maintainability.  
**Fix**: Rename to a descriptive name.  
**Example**:  
```python
app_state = AppState()
```
**Best Practice**: Use meaningful names for variables and classes.

---

### **5. Duplicate Code**  
**Issue**: `reset_state()` is duplicated in `main()`.  
**Impact**: Redundant logic.  
**Fix**: Move to a separate function.  
**Example**:  
```python
def reset_state():
    global app_state
    app_state = AppState()
```
**Best Practice**: Avoid duplication by encapsulating logic in functions.

---

### **Summary of Key Issues**  
| Smell Type | Priority | Impact | Recommendation |
|------------|----------|--------|------------------|
| Tight Coupling | High | Critical | Refactor state encapsulation. |
| Magic Numbers | Medium | Hard to understand | Use named constants. |
| Long Function | Medium | Difficult to read | Split into smaller functions. |
| Unclear Naming | Medium | Reduces clarity | Rename variables/classes. |
| Duplicate Code | Low | Minimal impact | Move logic to helper functions. |

---

### **Recommended Fixes**  
1. Encapsulate `GLOBAL_STATE` in a class.  
2. Extract constants into variables.  
3. Split `process_items()` into helper functions.  
4. Rename `GLOBAL_STATE` to a descriptive name.  
5. Move `reset_state()` to a separate function.