### **Code Smell Review Summary**

---

### **1. Code Smell Type**: Variable Naming Convention Violation  
**Problem Location**: `GLOBAL_TEXT`, `GLOBAL_COUNTER`, `GLOBAL_MODE`  
**Detailed Explanation**:  
- Variables are named with uppercase underscores, violating PEP8 and readability standards.  
- Example: `GLOBAL_TEXT` implies a global variable but lacks clarity.  

**Root Cause**: Lack of consistent naming conventions and lack of descriptive names.  

**Impact**: Reduced readability, maintenance challenges, and potential bugs.  

**Fix**: Rename variables to snake_case (e.g., `global_text`, `global_counter`).  

**Example**:  
```python
global_text = ""
global_counter = 0
global_mode = "default"
```

---

### **2. Code Smell Type**: Missing Docstrings  
**Problem Location**: `handle_btn1`, `handle_btn2`, `handle_btn3`  
**Detailed Explanation**:  
- Functions lack docstrings explaining purpose, parameters, and return values.  

**Root Cause**: Lack of documentation for business logic.  

**Impact**: Increased learning curve for developers and reduced trust in code.  

**Fix**: Add docstrings with `"""..."""`.  

**Example**:  
```python
def handle_btn1(self, text):
    """Update text area with 'Button 1 clicked'."""
    self.textArea.append("Button 1 clicked")
```

---

### **3. Code Smell Type**: Duplicated Logic  
**Problem Location**: `handle_btn1` and `handle_btn2`  
**Detailed Explanation**:  
- Similar logic for updating text and labels.  

**Root Cause**: Code duplication.  

**Impact**: Reduced maintainability and increased risk of errors.  

**Fix**: Extract shared logic into a helper method.  

**Example**:  
```python
def update_status(self, text):
    self.textArea.append(f"Added: {text}")
```

---

### **4. Code Smell Type**: Poor Naming Conventions  
**Problem Location**: `GLOBAL_TEXT`, `GLOBAL_COUNTER`, `GLOBAL_MODE`  
**Detailed Explanation**:  
- Variables lack clarity and are generic.  

**Root Cause**: No descriptive naming.  

**Impact**: Reduced code clarity.  

**Fix**: Use descriptive names.  

---

### **Best Practice Note**  
- **PEP8 Compliance**: Enforce snake_case for variables and docstrings.  
- **Documentation**: Add docstrings for functions and parameters.  
- **Encapsulation**: Avoid global variables and use class-level state.  

---

### **Summary of Recommendations**  
| Priority | Action | Example |  
|---------|--------|---------|  
| High | Rename variables | `global_text = ""` |  
| High | Add docstrings | `"""Update text area with 'Button 1 clicked'."""` |  
| Medium | Extract shared logic | `update_status()` |  
| Medium | Use descriptive names | `global_mode = "default"` |  

--- 

### **Final Output**  
- **Root Cause**: Inconsistent naming and lack of documentation.  
- **Impact**: Reduced maintainability and readability.  
- **Solution**: Enforce PEP8, add docstrings, and encapsulate logic.