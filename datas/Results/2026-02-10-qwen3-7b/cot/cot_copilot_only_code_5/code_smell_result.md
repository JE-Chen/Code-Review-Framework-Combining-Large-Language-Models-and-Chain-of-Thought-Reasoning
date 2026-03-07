### Code Smell Types & Details

---

**1. Code Smell Type**: Tight Coupling  
**Problem Location**: `GLOBAL_STATE` is used directly in all functions.  
**Detailed Explanation**: The state is a global variable shared across all functions. Changes propagate throughout the codebase, making it hard to isolate or test individual components.  
**Improvement Suggestions**: Encapsulate state in a class or use a module. Example: `class AppState` with `reset_state()` and `process_items()`.  
**Priority Level**: High  

---

**2. Code Smell Type**: Magic Numbers  
**Problem Location**: Constants like `77`, `21`, and `threshold` are hardcoded.  
**Detailed Explanation**: Values are arbitrary and not explained. They could be part of the design but lack documentation.  
**Improvement Suggestions**: Replace with variables or constants. Example: `THRESHOLD = 77`, `INITIAL_DATA_RANGE = (1, 21)`.  
**Priority Level**: Medium  

---

**3. Code Smell Type**: Long Function  
**Problem Location**: `process_items()` contains complex logic and nested conditions.  
**Detailed Explanation**: The function is too long to read and understand. It lacks clarity and separation of concerns.  
**Improvement Suggestions**: Break into smaller functions. Example: `process_even_odd()`, `process_threshold()`.  
**Priority Level**: Medium  

---

**4. Code Smell Type**: Unclear Naming  
**Problem Location**: `GLOBAL_STATE` is a global variable with no explanation.  
**Detailed Explanation**: The name is vague and does not reflect its purpose.  
**Improvement Suggestions**: Rename to `AppState` or `State`.  
**Priority Level**: Medium  

---

**5. Code Smell Type**: Duplicate Code  
**Problem Location**: `reset_state()` is called in `main()`.  
**Detailed Explanation**: The reset logic is duplicated in the main function.  
**Improvement Suggestions**: Move `reset_state()` to a separate function.  
**Priority Level**: Low  

---

### Summary of Key Issues
| Smell Type | Priority | Impact |
|------------|----------|--------|
| Tight Coupling | High | Critical for maintainability |
| Magic Numbers | Medium | Hard to understand |
| Long Function | Medium | Difficult to read |
| Unclear Naming | Medium | Reduces clarity |
| Duplicate Code | Low | Minimal impact |

---

### Recommended Fixes
1. Refactor `GLOBAL_STATE` into a class or module.  
2. Extract constants into variables.  
3. Break `process_items()` into smaller helper functions.  
4. Rename `GLOBAL_STATE` to a more descriptive name.  
5. Move `reset_state()` to a separate function.