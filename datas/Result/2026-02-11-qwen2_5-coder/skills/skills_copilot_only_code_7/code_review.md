### Diff #1 Summary
This PR introduces a simple GUI application using PySide6 that manages some global state variables (`GLOBAL_TEXT`, `GLOBAL_COUNTER`, `GLOBAL_MODE`) and updates the UI based on button clicks. The application has three buttons, an input field, a label, and a text area.

### Diff #1 Linting Issues
- **Issue**: Global variable usage.
  - **File**: `<filename>.py`
  - **Line**: Multiple lines within the `MainWindow` class methods.
  - **Explanation**: Using global variables can lead to hard-to-maintain and debug code.
  - **Suggestion**: Replace global variables with instance variables or use a dedicated data structure to encapsulate the state.

- **Issue**: Missing type hints.
  - **File**: `<filename>.py`
  - **Line**: Class definition and method signatures.
  - **Explanation**: Type hints help ensure type safety and improve code readability.
  - **Suggestion**: Add type hints for parameters and return values where applicable.

### Diff #1 Code Smells
- **Issue**: Long function.
  - **File**: `<filename>.py`
  - **Function**: `handle_btn2`
  - **Explanation**: Functions should be short and focused on a single responsibility. This makes them easier to understand and test.
  - **Recommendation**: Refactor `handle_btn2` into smaller functions, such as one for checking the counter value and another for appending messages to the text area.

- **Issue**: Poor naming.
  - **File**: `<filename>.py`
  - **Variable**: `GLOBAL_MODE`
  - **Explanation**: Variable names should be descriptive and follow PEP 8 guidelines.
  - **Recommendation**: Rename `GLOBAL_MODE` to something like `mode` or `view_mode`.

- **Issue**: Tight coupling.
  - **File**: `<filename>.py`
  - **Explanation**: The GUI logic is tightly coupled with the business logic, making it harder to change or reuse components independently.
  - **Recommendation**: Consider separating concerns by creating separate classes for the GUI and the business logic.