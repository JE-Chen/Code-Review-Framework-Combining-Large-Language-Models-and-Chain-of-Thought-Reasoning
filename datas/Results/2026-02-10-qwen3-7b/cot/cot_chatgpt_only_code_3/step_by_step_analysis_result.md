### Code Smell & Linter Analysis

---

### **1. Linter Message 1: `no-empty-blocks`**  
**Issue**: Block `if now is None` is empty.  
**Root Cause**: Missing logic or comment, leading to ambiguity.  
**Impact**: Reduces readability and increases maintenance burden.  
**Fix**: Add explicit `if`/`else` or comment.  
**Example**:  
```python
if now is None:
    raise ValueError("now must be provided")
else:
    # Proceed with logic
```

---

### **2. Linter Message 2: `no-duplicate-code`**  
**Issue**: `create_order` and `process_order` share similar logic.  
**Root Cause**: Repeated code fragments.  
**Impact**: Hard to maintain and test.  
**Fix**: Extract shared logic into helper functions.  
**Example**:  
```python
def _common_logic(order):
    # Shared code
```

---

### **3. Linter Message 3: `no-unused-vars`**  
**Issue**: `order` is unused in `process_order`.  
**Root Cause**: Redundant variable.  
**Impact**: Code smells and wasted resources.  
**Fix**: Remove or rename unused variable.  

---

### **4. Linter Message 5: `no-implicit-boolean`**  
**Issue**: Boolean expressions lack explicit `if/else`.  
**Root Cause**: Code is too concise.  
**Impact**: Hard to understand and maintain.  
**Fix**: Add explicit conditions.  
**Example**:  
```python
if total > 1000:
    apply_discount()
else:
    log_error()
```

---

### **Root Cause & Recommendations**  
- **Root Cause**: Overly complex logic, poor naming, and duplicated code.  
- **Recommendations**:  
  1. Extract helper functions and refactor `process_order`.  
  2. Define constants for discounts.  
  3. Add docstrings and comments.  
  4. Refactor variable names.  

---

### **Impact Summary**  
- **Readability**: Improved with clearer logic and comments.  
- **Maintainability**: Reduced duplication and complexity.  
- **Scalability**: Easier to extend or modify.  

--- 

### **Best Practice Note**  
- **SOLID Principle**: Keep functions small and focused.  
- **DRY Principle**: Avoid duplicated code and logic.