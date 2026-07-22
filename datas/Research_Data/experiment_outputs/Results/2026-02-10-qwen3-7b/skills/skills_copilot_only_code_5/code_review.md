### Diff #1
---

### 1. Summary
- **Purpose**: The code manages a simple data processing flow with global state and basic functions.  
- **Affected Files**: `main.py`.  
- **Plain-Language Explanation**: The code initializes data, toggles flags, processes items, and resets state in a simple loop.  

---

### 2. Linting Issues
- **Violation**: Global variables (`GLOBAL_STATE`) are used without scoping.  
- **Fix**: Use local variables or encapsulate state in classes.  
- **File**: `main.py`, line 12.  
- **Violation**: No function parameters used.  
- **Fix**: Add parameters to functions.  
- **File**: `main.py`, line 20.  

---

### 3. Code Smells
- **Global State**: `GLOBAL_STATE` is used across multiple functions, making it hard to test and maintain.  
- **Tight Coupling**: Functions rely on global state without encapsulation.  
- **Poor Naming**: `toggle_flag()` is unclear.  
- **Fix**: Encapsulate state in a class or use local variables.  
- **Example**: Replace `GLOBAL_STATE` with a class or pass state as parameters.