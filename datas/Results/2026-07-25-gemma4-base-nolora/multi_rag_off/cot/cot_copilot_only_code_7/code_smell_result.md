- Code Smell Type: Use of Global State
- Problem Location: `GLOBAL_TEXT`, `GLOBAL_COUNTER`, `GLOBAL_MODE` and the `global` keywords inside `handle_btn1`, `handle_btn2`, and `handle_btn3`.
- Detailed Explanation: The application relies on global variables to maintain state. This creates tight coupling between the logic and the global scope, making the code difficult to test (unit tests will interfere with each other), prone to side-effect bugs, and impossible to instantiate multiple `MainWindow` objects independently.
- Improvement Suggestions: Move these variables into the `MainWindow` class as instance attributes (e.g., `self.text`, `self.counter`, `self.mode`) initialized in the `__init__` method.
- Priority Level: High

- Code Smell Type: Unclear Naming
- Problem Location: `btn1`, `btn2`, `btn3`, `input1`, `label1`, `handle_btn1`, `handle_btn2`, `handle_btn3`.
- Detailed Explanation: The naming convention is generic and non-descriptive. Names like `btn1` or `handle_btn1` provide no semantic meaning regarding the purpose of the widget or the action being performed. This forces developers to read the implementation details to understand the UI flow, reducing maintainability.
- Improvement Suggestions: Rename variables to reflect their purpose:
    - `btn1` $\rightarrow$ `add_text_button` / `handle_btn1` $\rightarrow$ `on_add_text_clicked`
    - `btn2` $\rightarrow$ `show_counter_button` / `handle_btn2` $\rightarrow$ `on_show_counter_clicked`
    - `btn3` $\rightarrow$ `reset_button` / `handle_btn3` $\rightarrow$ `on_reset_clicked`
    - `input1` $\rightarrow$ `text_input`
    - `label1` $\rightarrow$ `status_label`
- Priority Level: Medium

- Code Smell Type: Violation of Single Responsibility Principle (SRP)
- Problem Location: `MainWindow` class.
- Detailed Explanation: The `MainWindow` class is handling three distinct responsibilities: defining the UI layout, managing the application state (business logic), and handling user interaction. As the application grows, this class will become a "God Object," making it fragile and difficult to modify.
- Improvement Suggestions: Separate the concerns by implementing a simple Model-View-Controller (MVC) or Model-View-Presenter (MVP) pattern. Create a separate `AppState` or `Controller` class to handle the logic for counting and text manipulation, leaving `MainWindow` to handle only the display and event forwarding.
- Priority Level: Medium

- Code Smell Type: Deeply Nested Conditional Logic (Arrow Anti-pattern)
- Problem Location: `handle_btn2` method.
- Detailed Explanation: The method uses nested `if/else` blocks to determine which message to display. While small here, this pattern leads to "cyclomatic complexity" where the logic becomes hard to follow and test as more conditions are added.
- Improvement Suggestions: Use "Guard Clauses" to return early or flatten the logic. For example, handle the `GLOBAL_COUNTER <= 5` case first and return, then handle the `GLOBAL_MODE` logic separately.
- Priority Level: Low