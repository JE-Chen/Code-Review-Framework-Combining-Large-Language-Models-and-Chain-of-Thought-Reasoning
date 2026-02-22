### Code Smell Type: Global State Usage
- **Problem Location**: Lines 6–8, `handle_btn1`, `handle_btn2`, `handle_btn3`
- **Detailed Explanation**: The use of global variables (`GLOBAL_TEXT`, `GLOBAL_COUNTER`, `GLOBAL_MODE`) violates encapsulation principles. These shared mutable states make code harder to reason about, debug, and test in isolation. It introduces hidden dependencies between functions and increases risk of side effects.
- **Improvement Suggestions**:
  - Replace global variables with instance attributes (`self.text`, `self.counter`, etc.) within the `MainWindow` class.
  - Encapsulate state management logic inside methods or helper classes.
- **Priority Level**: High

---

### Code Smell Type: Magic Strings
- **Problem Location**: Line 10 (`"default"`), Line 29 (`"default"`), Line 32 (`"reset"`)
- **Detailed Explanation**: Hardcoded string literals like `"default"` and `"reset"` reduce readability and maintainability. If these values change, they must be updated in multiple places, increasing the chance of inconsistencies.
- **Improvement Suggestions**:
  - Define constants at module or class level for such strings.
  - Use an enum or configuration object to manage valid modes.
- **Priority Level**: Medium

---

### Code Smell Type: Long Method
- **Problem Location**: `handle_btn2` method (lines 27–36)
- **Detailed Explanation**: This method contains nested conditional logic that makes it hard to read and understand. It checks multiple conditions without clear separation of concerns, violating the Single Responsibility Principle.
- **Improvement Suggestions**:
  - Extract sub-methods for checking counter thresholds and mode-specific behavior.
  - Simplify nested conditionals using early returns or guard clauses.
- **Priority Level**: High

---

### Code Smell Type: Duplicated Logic
- **Problem Location**: Lines 21 and 30 in `handle_btn1` and `handle_btn2`
- **Detailed Explanation**: The pattern of appending messages to `textArea` appears repeatedly. Repeating similar code blocks reduces maintainability and increases chances of inconsistency when updating display logic.
- **Improvement Suggestions**:
  - Create a helper method like `_append_message(message)` to centralize UI updates.
- **Priority Level**: Medium

---

### Code Smell Type: Inconsistent Naming
- **Problem Location**: Variable names (`btn1`, `btn2`, `btn3`, `input1`, `label1`, `textArea`)
- **Detailed Explanation**: Non-descriptive names like `btn1`, `input1` do not reflect their purpose. While acceptable for prototyping, this hinders understanding and collaboration in larger teams.
- **Improvement Suggestions**:
  - Rename components to describe their functionality (e.g., `add_text_button`, `counter_display_label`).
- **Priority Level**: Medium

---

### Code Smell Type: Tight Coupling
- **Problem Location**: All handlers accessing shared global state directly
- **Detailed Explanation**: Each handler modifies and reads from the same global scope, creating tight coupling among components. This makes unit testing difficult and increases brittleness.
- **Improvement Suggestions**:
  - Introduce a dedicated model class to hold application data and provide controlled access via methods.
- **Priority Level**: High

---

### Code Smell Type: Lack of Input Validation
- **Problem Location**: Line 20 in `handle_btn1`
- **Detailed Explanation**: Although a check for empty input exists, there's no validation on other inputs (like special characters). Without sanitization, unexpected behavior or vulnerabilities may arise.
- **Improvement Suggestions**:
  - Add more robust input validation and sanitization where needed.
  - Consider defining allowed input formats or ranges.
- **Priority Level**: Medium

---

### Code Smell Type: Poor Separation of Concerns
- **Problem Location**: Class `MainWindow` combines UI setup, event handling, and business logic
- **Detailed Explanation**: Mixing UI rendering logic with core application logic reduces modularity and reusability. This makes future enhancements or switching frameworks harder.
- **Improvement Suggestions**:
  - Separate UI elements into widgets and delegate logic to a separate controller or model layer.
- **Priority Level**: High

---