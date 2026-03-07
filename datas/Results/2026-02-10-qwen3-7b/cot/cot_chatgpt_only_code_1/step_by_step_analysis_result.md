### **Code Smell & Linter Analysis**

---

### **1. Core Issues & Root Causes**  
#### **Issue 1**: Global Variable `total_result`  
- **Problem**: Used in `doStuff` but not declared/used in the function.  
- **Root Cause**: Lack of encapsulation and poor state management.  
- **Impact**: Hard to test, side effects, and reduced clarity.  

#### **Issue 2**: Unused Variable `z`  
- **Problem**: Unreferenced in `doStuff`.  
- **Root Cause**: Poor code design or redundant logic.  
- **Impact**: Reduces readability and increases maintenance burden.  

#### **Issue 3**: Redundant Nested Conditions  
- **Problem**: Deeply nested `if` statements.  
- **Root Cause**: Poor code organization and lack of helper functions.  
- **Impact**: Increases cognitive load and reduces maintainability.  

#### **Issue 4**: Unused Imports  
- **Problem**: `math` and `time` imports not used.  
- **Root Cause**: Unnecessary code bloat.  
- **Impact**: Poor code cleanliness and slower execution.  

#### **Issue 5**: Redundant `collectValues` Calls  
- **Problem**: Calls to `collectValues` in `main`.  
- **Root Cause**: Over-engineering or misplaced logic.  
- **Impact**: Reduces code efficiency.  

---

### **2. Impact Assessment**  
| Issue | Risk Level | Explanation |  
|------|------------|-------------|  
| Global State | High | Side effects, testability issues. |  
| Unused Variables | Medium | Reduced clarity and maintainability. |  
| Redundant Logic | High | Increased cognitive load and code complexity. |  

---

### **3. Suggested Fixes**  
#### **1. Avoid Global State**  
- **Fix**: Pass `total_result` as a parameter.  
- **Example**:  
  ```python
  def doStuff(total_result, x, y):
      # Use total_result instead of global variable
  ```  

#### **2. Remove Unused Variables**  
- **Fix**: Eliminate `z` or re-use it.  
- **Example**:  
  ```python
  # Remove unused variable
  # z = ...  # Not used
  ```  

#### **3. Simplify Logic**  
- **Fix**: Extract helper functions and remove nested conditions.  
- **Example**:  
  ```python
  def process_data(x, y):
      return calculate_value(x) if condition else 0
  ```  

#### **4. Remove Unused Imports**  
- **Fix**: Delete unused imports.  

#### **5. Eliminate Redundant Calls**  
- **Fix**: Use `collectValues` only where needed.  

---

### **4. Best Practice Notes**  
- **SOLID Principle**: Encapsulate logic in functions and avoid global state.  
- **DRY Principle**: Extract repeated calculations into helper functions.  
- **Naming Conventions**: Use meaningful variable and function names.  

---

### **Summary of Key Fixes**  
| Problem | Fix | Priority |  
|--------|-----|----------|  
| Global state | Pass parameters | High |  
| Unused variables | Remove | Medium |  
| Redundant logic | Extract helpers | High |  

--- 

### **Final Recommendation**  
Refactor `doStuff` to extract helpers, remove global variables, and simplify logic. Prioritize readability and maintainability.