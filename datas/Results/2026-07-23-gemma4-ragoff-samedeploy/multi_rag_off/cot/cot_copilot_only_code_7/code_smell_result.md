- Code Smell Type: Use of Global State
- Problem Location: `GLOBAL_TEXT`, `GLOBAL_COUNTER`, `GLOBAL_MODE` and the `global` keywords inside `handle_btn1`, `handle_btn2`, and `handle_btn3`.
- Detailed Explanation: The application relies on global variables to maintain state. This creates tight coupling between the logic and the global scope, making the code difficult to test in isolation, prone to side-effect bugs, and impossible to instantiate multiple `MainWindow` instances independently.
- Improvement Suggestions: Move these variables into the `MainWindow` class as instance attributes (e.g., `self.text`, `self.counter`, `self.mode`) initialized in the `__init__` method.
- Priority Level: High

- Code Smell Type: Unclear Naming
- Problem Location: `btn1`, `btn2`, `btn3`, `input1`, `label1`, `handle_btn1`, `handle_btn2`, `handle_btn3`.
- Detailed Explanation: Generic names like `btn1` or `handle_btn1` provide no semantic meaning. A developer reading the code must trace the UI initialization to understand that `btn1` is actually the "Add Text" button. This reduces readability and increases the likelihood of errors during maintenance.
- Improvement Suggestions: Rename variables to reflect their purpose:
    - `btn1` $\rightarrow$ `add_text_button`
    - `input1` $\rightarrow$ `text_input`
    - `handle_btn1` $\rightarrow$ `on_add_text_clicked`
- Priority Level: Medium

- Code Smell Type: Violation of Single Responsibility Principle (SRP)
- Problem Location: `MainWindow` class (specifically the `handle_btn` methods).
- Detailed Explanation: The `MainWindow` class is handling both the UI layout/presentation and the business logic (state management and conditional logic for the counter). As the application grows, this class will become a "God Object," making it hard to maintain or modify the logic without breaking the UI.
- Improvement Suggestions: Separate the business logic into a separate Controller or Model class. The `MainWindow` should only handle UI events and call methods on a logic handler to update the state.
- Priority Level: Medium

- Code Smell Type: Deeply Nested Conditionals (Arrow Anti-pattern)
- Problem Location: `handle_btn2` method.
- Detailed Explanation: The nested `if/else` blocks (checking `GLOBAL_COUNTER > 5`, then `GLOBAL_MODE`, then `GLOBAL_COUNTER % 2`) make the logic harder to follow and increase cognitive load.
- Improvement Suggestions: Use guard clauses to return early or flatten the logic. For example, handle the `GLOBAL_COUNTER <= 5` case first and return, then handle the mode-specific logic.
- Priority Level: Low