- Code Smell Type: Use of Global State
- Problem Location: `GLOBAL_TEXT`, `GLOBAL_COUNTER`, `GLOBAL_MODE` and the `global` keywords inside `handle_btn1`, `handle_btn2`, and `handle_btn3`.
- Detailed Explanation: The application relies on global variables to maintain state. This creates tight coupling between the logic and the global scope, making the code difficult to test in isolation and prone to side-effect bugs. If multiple windows were opened, they would all share and overwrite the same state, leading to unpredictable behavior.
- Improvement Suggestions: Encapsulate these variables as instance attributes within the `MainWindow` class (e.g., `self.text`, `self.counter`, `self.mode`) or move them into a dedicated State/Model class.
- Priority Level: High

- Code Smell Type: Unclear Naming
- Problem Location: `btn1`, `btn2`, `btn3`, `input1`, `label1`, `handle_btn1`, `handle_btn2`, `handle_btn3`.
- Detailed Explanation: The naming is generic and based on the order of creation rather than the purpose of the components. This forces a developer to read the button labels or the function implementation to understand what the code is doing, reducing maintainability and readability.
- Improvement Suggestions: Rename variables to reflect their intent. For example:
    - `btn1` $\rightarrow$ `add_text_button`
    - `input1` $\rightarrow$ `text_input_field`
    - `handle_btn1` $\rightarrow$ `on_add_text_clicked`
- Priority Level: Medium

- Code Smell Type: Deeply Nested Conditional Logic (Arrow Anti-pattern)
- Problem Location: `handle_btn2` method.
- Detailed Explanation: The method uses multiple levels of nested `if/else` statements to determine which message to append. As more modes or conditions are added, this will become increasingly difficult to read and maintain.
- Improvement Suggestions: Use guard clauses to handle the "small counter" case early and return. For the mode-specific logic, consider a dictionary mapping or a simple strategy pattern if the logic grows further.
- Priority Level: Low