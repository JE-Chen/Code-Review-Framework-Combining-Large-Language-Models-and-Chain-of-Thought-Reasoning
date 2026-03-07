### PR Summary Template

- **Key Changes**: Added `CustomWidget` with buttons and text area, and `MainWindow` that hosts it.  
- **Impact Scope**: Affected `BaseWindow`, `CustomWidget`, and `MainWindow` classes.  
- **Purpose**: Improve UI interactivity and input validation.  
- **Risks**: Potential issues with text length logic or missing edge cases.  
- **Confirm Items**: Docstrings, tests, and edge case validation.  

---

### Code Review Details

#### 1. **Readability & Consistency**  
- ✅ Indentation matches Python standards (4 spaces).  
- ⚠️ Suggest: Add spacing around operators (e.g., `self.btnA.clicked.connect(self.handle_btnA)`).  
- ⚠️ Suggest: Use `self.label_text` instead of `self.labelX` for clarity.  

---

#### 2. **Naming Conventions**  
- ✅ Class names (`BaseWindow`, `CustomWidget`, `MainWindow`) follow CamelCase.  
- ⚠️ Suggestion: Add `handle_button_click` to methods (e.g., `handle_btnA` → `handle_button_click`).  

---

#### 3. **Software Engineering Standards**  
- ✅ Modular structure with separation of concerns.  
- ⚠️ Suggestion: Extract `handle_btnA`/`handle_btnB` into helper methods.  
- ⚠️ Suggestion: Add validation for empty text in `handle_btnB`.  

---

#### 4. **Logic & Correctness**  
- ✅ Text length logic is clear and handles edge cases.  
- ⚠️ Suggestion: Add `text.strip()` before length checks to avoid whitespace issues.  

---

#### 5. **Performance & Security**  
- ✅ No performance bottlenecks.  
- ⚠️ Suggestion: Validate input types (e.g., ensure `textArea.toPlainText()` is non-empty).  

---

#### 6. **Documentation & Testing**  
- ⚠️ Missing docstrings for classes/methods.  
- ⚠️ No unit tests for edge cases (e.g., empty text, invalid lengths).  

---

#### 7. **Scoring & Feedback Style**  
- ✅ Balanced focus on clarity and completeness.