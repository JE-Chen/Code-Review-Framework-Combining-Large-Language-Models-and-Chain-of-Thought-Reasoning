### Code Smell Review

---

### **1. Code Smell Type**: Long Functionality in Methods  
**Problem Location**: `handle_btnA` and `handle_btnB` methods  
**Detailed Explanation**: These methods encapsulate multiple responsibilities (text validation, label updates) and lack separation into smaller, focused functions. This reduces readability and reusability.  
**Improvement Suggestions**: Extract logic into helper methods (e.g., `update_label()`).  
**Priority Level**: Medium  

---

### **2. Code Smell Type**: Duplicate Layout Construction  
**Problem Location**: Layout creation in `CustomWidget`  
**Detailed Explanation**: The same layout structure is repeated in `CustomWidget`, leading to redundancy.  
**Improvement Suggestions**: Extract layout creation into a helper method (e.g., `build_layout()`).  
**Priority Level**: Medium  

---

### **3. Code Smell Type**: Unclear Naming of Methods  
**Problem Location**: Methods like `handle_btnA` and `handle_btnB`  
**Detailed Explanation**: Method names are descriptive but could be more explicit.  
**Improvement Suggestions**: Rename to `handle_button_click()` or similar.  
**Priority Level**: Low  

---

### **4. Code Smell Type**: Magic Numbers in Layout  
**Problem Location**: Layout positions (e.g., `0`, `1`, `2`)  
**Detailed Explanation**: Hard-coded values lack semantic clarity.  
**Improvement Suggestions**: Replace with descriptive strings (e.g., `"btnA"`, `"btnB"`).  
**Priority Level**: Low  

---

### **5. Code Smell Type**: Lack of Comments  
**Problem Location**: Complex logic without inline comments  
**Detailed Explanation**: Comments are sparse, reducing maintainability.  
**Improvement Suggestions**: Add inline comments for critical logic.  
**Priority Level**: Low  

---

### **6. Code Smell Type**: Tight Coupling Between Widgets  
**Problem Location**: `MainWindow` and `CustomWidget`  
**Detailed Explanation**: `MainWindow` tightly couples with `CustomWidget`, limiting testability.  
**Improvement Suggestions**: Decouple via dependency injection or event-driven architecture.  
**Priority Level**: Medium  

---

### **Summary of Key Issues**  
| Smell Type | Priority | Impact | Recommendation |
|------------|----------|--------|------------------|
| Long Methods | Medium | Reduces readability | Extract logic |
| Duplicate Layout | Medium | Increases complexity | Extract layout |
| Unclear Naming | Low | Hinders understanding | Rename methods |
| Magic Numbers | Low | Reduces clarity | Use descriptive values |
| Lack of Comments | Low | Limits maintainability | Add comments |

---

### **Final Recommendation**  
Refactor `CustomWidget` to extract layout and helper methods, improve method names, and add inline comments. Maintain separation of concerns and modular design.