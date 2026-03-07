### Diff #1: New file `gui.py`

---

### **Summary**
- **Purpose**: Creates a simple GUI application with two buttons and a label that updates text on clicks.  
- **Scope**: Entire file (`gui.py`), introducing global state, a monolithic UI setup function, and nested event handlers.  
- **Plain language**: This code builds a window with two buttons. Clicking them changes a label’s text, but the implementation is messy and hard to understand or maintain.  

---

### **Linting Issues**
- **Global variables** (`globalLabel`, `anotherGlobal`):  
  - *Violation*: Declared at module level without clear justification.  
  - *Fix*: Remove globals; pass state explicitly via class methods.  
- **Unused variable** (`anotherGlobal`):  
  - *Violation*: Defined but never used.  
  - *Fix*: Delete the line.  
- **Overly long function name** (`veryStrangeFunctionNameThatDoesTooMuch`):  
  - *Violation*: Exceeds 50 characters; obscures intent.  
  - *Fix*: Rename to `setup_ui` or similar.  
- **Redundant text in button handlers**:  
  - *Violation*: `btn1` has two identical `setText` calls.  
  - *Fix*: Remove duplicate connection.  

---

### **Code Smells**
- **Global state abuse** (`globalLabel`):  
  - *Why problematic*: Makes `veryStrangeFunctionNameThatDoesTooMuch` dependent on external state. Breaks testability and reusability.  
  - *Fix*: Return the label from the function or bind it to the window instance.  
- **Function does too much**:  
  - *Why problematic*: Creates UI, handles events, and manages state in one function. Violates Single Responsibility Principle.  
  - *Fix*: Split into `create_ui`, `handle_btn1_click`, etc.  
- **Dead code** (`anotherGlobal`):  
  - *Why problematic*: Clutters the file with irrelevant code.  
  - *Fix*: Delete the unused variable.  
- **Nesting without purpose** (`inner`/`inner2`):  
  - *Why problematic*: Adds complexity for no benefit (e.g., `inner2` is called immediately).  
  - *Fix*: Inline the logic or remove the nesting.  
- **Hardcoded strings**:  
  - *Why problematic*: Blocks localization and increases duplication risk.  
  - *Fix*: Extract strings to constants or resource files.  

---

### **Key Recommendations**
1. **Eliminate globals** – Use instance attributes instead.  
2. **Split monolithic function** – Separate UI setup from event handling.  
3. **Remove dead code** – Delete `anotherGlobal`.  
4. **Simplify event handlers** – Avoid redundant connections.  
5. **Rename with clarity** – Replace `veryStrangeFunctionNameThatDoesTooMuch` with `setup_ui`.