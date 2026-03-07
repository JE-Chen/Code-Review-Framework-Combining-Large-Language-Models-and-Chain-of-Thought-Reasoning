### Code Smell Type: Deeply Nested Conditionals
**Problem Location:**  
```python
def handle_btnB(self):
    text = self.textArea.toPlainText()
    if text:
        if len(text) < 5:
            self.labelX.setText("Short")
        else:
            if len(text) < 10:
                self.labelX.setText("Medium")
            else:
                if len(text) < 20:
                    self.labelX.setText("Long")
                else:
                    self.labelX.setText("Very Long")
    else:
        self.labelX.setText("No Input")
```

**Detailed Explanation:**  
This method exhibits excessive nesting (3 levels deep), violating readability and maintainability principles. Deep nesting makes the code harder to follow, increases cognitive load, and risks introducing bugs during modifications. The structure also lacks a clear exit point for the "empty text" case, forcing readers to mentally track nested scopes. This violates the Single Responsibility Principle (SRP) by combining text validation and UI updates.

**Improvement Suggestions:**  
Refactor into linear conditional checks with early returns:
```python
def handle_btnB(self):
    text = self.textArea.toPlainText()
    if not text:
        self.labelX.setText("No Input")
        return
        
    length = len(text)
    if length < 5:
        self.labelX.setText("Short")
    elif length < 10:
        self.labelX.setText("Medium")
    elif length < 20:
        self.labelX.setText("Long")
    else:
        self.labelX.setText("Very Long")
```
*Move category logic to a dedicated utility class if reused elsewhere.*

**Priority Level:** High

---

### Code Smell Type: Magic Numbers
**Problem Location:**  
```python
if len(text) < 5:  # 5
elif len(text) < 10:  # 10
elif len(text) < 20:  # 20
```

**Detailed Explanation:**  
Hardcoded thresholds (5, 10, 20) lack context, making the code unself-documenting. Changing these values requires searching through all conditional branches, increasing maintenance risk. The numbers also conflict with the `handle_btnA` logic (which uses `len(text) > 0` instead of explicit length checks), creating inconsistency.

**Improvement Suggestions:**  
Define named constants at the class level:
```python
class CustomWidget(QWidget):
    SHORT_THRESHOLD = 5
    MEDIUM_THRESHOLD = 10
    LONG_THRESHOLD = 20
    
    def handle_btnB(self):
        text = self.textArea.toPlainText()
        if not text:
            self.labelX.setText("No Input")
            return
            
        length = len(text)
        if length < self.SHORT_THRESHOLD:
            self.labelX.setText("Short")
        elif length < self.MEDIUM_THRESHOLD:
            self.labelX.setText("Medium")
        elif length < self.LONG_THRESHOLD:
            self.labelX.setText("Long")
        else:
            self.labelX.setText("Very Long")
```

**Priority Level:** Medium

---

### Code Smell Type: Inconsistent Naming Conventions
**Problem Location:**  
`handle_btnA`, `handle_btnB` vs. `btnA`, `btnB`

**Detailed Explanation:**  
The prefix `handle_` implies a naming pattern for event handlers, but the suffixes (`btnA`, `btnB`) are ambiguous. This creates confusion about whether the names refer to the button *controls* or their *functions*. In contrast, `handle_btnB` suggests the handler is for button B, but the variable name `btnB` already identifies the button. The inconsistency forces readers to mentally map names to functionality.

**Improvement Suggestions:**  
Rename handlers to reflect behavior instead of button IDs:
```python
# Before
def handle_btnA(self): ...

# After
def update_text_length_display(self): ...

# Or (preferred for clarity)
def on_text_area_changed(self): ...  # If logic is tied to text area
```
*Use consistent naming: `on_button_X_clicked` for handlers, `btn_X` for controls.*

**Priority Level:** Medium

---

### Code Smell Type: Missing Documentation
**Problem Location:**  
Entire class and method definitions lack docstrings.

**Detailed Explanation:**  
No documentation explains:
- Purpose of `CustomWidget` (e.g., "Displays text length categorization")
- Behavior of handlers (e.g., "Updates label with text length category")
- Expected input/output for methods
This impedes onboarding and maintenance, especially for new developers unfamiliar with the GUI flow.

**Improvement Suggestions:**  
Add docstrings to all public members:
```python
class CustomWidget(QWidget):
    """Custom widget displaying text length and category.
    
    Includes buttons to trigger text analysis and a label for results.
    """
    
    def handle_btnB(self):
        """Updates label with text category based on length.
        
        Args:
            text (str): Current text in the text area.
        """
        # ... implementation ...
```

**Priority Level:** Medium

---

### Code Smell Type: Redundant Condition Logic
**Problem Location:**  
`handle_btnA` uses `len(text) > 0` while `handle_btnB` uses `if text:`.

**Detailed Explanation:**  
The `handle_btnA` condition is redundant since empty strings evaluate to `False`. The inconsistent style (length-based check vs. truthiness check) creates cognitive friction. Both methods should use the same idiomatic approach for empty string checks.

**Improvement Suggestions:**  
Standardize to truthiness checks:
```python
def handle_btnA(self):
    text = self.textArea.toPlainText()
    if text:
        self.labelX.setText("Length: " + str(len(text)))
    else:
        self.labelX.setText("Empty!")
```

**Priority Level:** Low

---

### Code Smell Type: Tight Coupling to UI
**Problem Location:**  
Handlers directly manipulate `self.labelX` and `self.textArea`.

**Detailed Explanation:**  
The business logic (text categorization) is entangled with UI details, making it impossible to test without a GUI framework. This violates testability principles and reduces code reuse. The same logic cannot be used in a non-GUI context.

**Improvement Suggestions:**  
Decouple logic from UI:
```python
class TextCategorizer:
    @staticmethod
    def get_category(text: str) -> str:
        if not text:
            return "No Input"
        length = len(text)
        if length < 5:
            return "Short"
        elif length < 10:
            return "Medium"
        elif length < 20:
            return "Long"
        else:
            return "Very Long"

# In CustomWidget:
def handle_btnB(self):
    text = self.textArea.toPlainText()
    self.labelX.setText(TextCategorizer.get_category(text))
```
*This enables unit testing of `TextCategorizer`.*

**Priority Level:** High