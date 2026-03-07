### Code Smell Review

---

### **1. Code Smell Type**: Use of Global Variables  
**Problem Location**: `handle_btn1`, `handle_btn2`, `handle_btn3`  
**Detailed Explanation**:  
- Global variables (`GLOBAL_TEXT`, `GLOBAL_COUNTER`, `GLOBAL_MODE`) are used in multiple functions without encapsulation.  
- They are not properly scoped, leading to side effects and difficulty in testing/maintaining.  
- Example: `GLOBAL_COUNTER` is modified in multiple functions without validation or isolation.  

**Improvement Suggestions**:  
- Replace global variables with class variables or pass them as parameters.  
- Example: Use `self.text_area` instead of `GLOBAL_TEXT`.  

**Priority Level**: High  

---

### **2. Code Smell Type**: Lack of Proper Encapsulation  
**Problem Location**: `handle_btn1`, `handle_btn2`, `handle_btn3`  
**Detailed Explanation**:  
- Global variables are not encapsulated within the `MainWindow` class.  
- Side effects risk propagating across the codebase.  

**Improvement Suggestions**:  
- Encapsulate variables in the class (e.g., `self._global_text`, `self._global_counter`).  
- Example: Use `self._global_text = ""` instead of `GLOBAL_TEXT`.  

**Priority Level**: High  

---

### **3. Code Smell Type**: Duplicated Logic  
**Problem Location**: `handle_btn1` and `handle_btn2`  
**Detailed Explanation**:  
- Both functions update the text area and label with similar logic.  
- Code duplication reduces maintainability and increases risk of errors.  

**Improvement Suggestions**:  
- Extract shared logic into a helper method (e.g., `update_status()`).  
- Example: `self.textArea.append("Added: " + text)` is reused.  

**Priority Level**: Medium  

---

### **4. Code Smell Type**: Poor Naming Conventions  
**Problem Location**: `GLOBAL_TEXT`, `GLOBAL_COUNTER`, `GLOBAL_MODE`  
**Detailed Explanation**:  
- Variable names are generic and lack clarity.  
- Example: `GLOBAL_COUNTER` implies a counter, but its purpose is unclear.  

**Improvement Suggestions**:  
- Use descriptive names (e.g., `global_text`, `global_counter`, `global_mode`).  
- Example: `global_text = ""` instead of `GLOBAL_TEXT`.  

**Priority Level**: Medium  

---

### **5. Additional Observations**  
- **Comments**: Minimal comments are present.  
- **Test Coverage**: No unit tests are shown.  
- **Refactor Opportunities**: Extract helper methods and improve encapsulation.  

---

### **Summary of Code Smells**  
| Smell Type | Priority | Impact | Recommendation |
|------------|----------|--------|-----------------|
| Global Variables | High | Side effects, testability | Replace with class variables |
| Lack of Encapsulation | High | Side effects, maintenance | Encapsulate in class |
| Duplicated Logic | Medium | Reduced maintainability | Extract shared logic |
| Poor Naming | Medium | Clarity issues | Use descriptive names |