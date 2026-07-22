- Code Smell Type: Unclear Naming
- Problem Location: `def veryStrangeFunctionNameThatDoesTooMuch(window):`
- Detailed Explanation: The function name is non-descriptive and explicitly admits to violating the Single Responsibility Principle. In a professional codebase, names should describe the *intent* and *action* of the function (e.g., `setup_main_layout`).
- Improvement Suggestions: Rename the function to something descriptive, such as `initialize_ui_components` or `setup_window_layout`.
- Priority Level: Medium

- Code Smell Type: Use of Global State
- Problem Location: `globalLabel = None`, `anotherGlobal = "Hello"`, and `global globalLabel`
- Detailed Explanation: Using global variables for UI components creates tight coupling and makes the code difficult to test and maintain. It can lead to unpredictable behavior if multiple windows are instantiated or if the state is modified from different parts of the application.
- Improvement Suggestions: Encapsulate the label and other state variables as instance attributes of the `MyWeirdWindow` class (e.g., `self.label = lbl`).
- Priority Level: High

- Code Smell Type: Violation of Single Responsibility Principle (SRP)
- Problem Location: `veryStrangeFunctionNameThatDoesTooMuch(window)`
- Detailed Explanation: This function is handling layout creation, widget instantiation, and business logic (event handling/callbacks) all in one place. This makes the code harder to refactor and reuse.
- Improvement Suggestions: Split the function into smaller, focused methods: one for creating widgets, one for setting up the layout, and one for defining signal-slot connections.
- Priority Level: Medium

- Code Smell Type: Unnecessary Nesting (Over-engineering)
- Problem Location: 
```python
def inner():
    def inner2():
        lbl.setText("巢狀函式被呼叫")
    inner2()
```
- Detailed Explanation: The use of a function inside a function inside another function to perform a simple label update is redundant and reduces readability without providing any functional benefit (like closure state management).
- Improvement Suggestions: Replace the nested functions with a single named method or a simple lambda if the logic remains this trivial.
- Priority Level: Low