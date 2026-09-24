- Code Smell Type: Unclear Naming
- Problem Location: `def veryStrangeFunctionNameThatDoesTooMuch(window):`
- Detailed Explanation: The function name is non-descriptive and explicitly admits to violating the Single Responsibility Principle. In a professional codebase, names should describe *what* the function does (e.g., `setup_main_layout`), not *how* the developer feels about the function. This hinders maintainability and readability.
- Improvement Suggestions: Rename the function to something descriptive, such as `setup_ui_components` or `initialize_layout`.
- Priority Level: Medium

- Code Smell Type: Violation of Single Responsibility Principle (SRP) & Tight Coupling
- Problem Location: `def veryStrangeFunctionNameThatDoesTooMuch(window):`
- Detailed Explanation: This function is acting as a "God Function" for the UI setup. It handles widget instantiation, layout management, and business logic (event handling/lambda functions) all in one place. Furthermore, it modifies the `window` object passed to it from the outside, creating tight coupling between the function and the `QWidget` subclass.
- Improvement Suggestions: Move the UI setup logic into the `MyWeirdWindow` class as a method (e.g., `self._init_ui()`). Separate the creation of widgets from the definition of their behavior.
- Priority Level: High

- Code Smell Type: Use of Global State
- Problem Location: `globalLabel = None` and `global globalLabel`
- Detailed Explanation: The use of `global` variables to track UI components is a dangerous practice. It makes the code harder to test, prevents the application from supporting multiple windows of the same type, and can lead to unpredictable side effects and memory leaks in GUI frameworks.
- Improvement Suggestions: Store the label as an instance attribute of the class (e.g., `self.label = QLabel(...)`) instead of using a global variable.
- Priority Level: High

- Code Smell Type: Unnecessary Complexity (Deep Nesting)
- Problem Location: 
  ```python
  def inner():
      def inner2():
          lbl.setText("巢狀函式被呼叫")
      inner2()
  ```
- Detailed Explanation: The use of a function defined inside a function, which then defines another function, is completely unnecessary here. This increases cognitive load and makes the execution flow harder to follow without providing any functional benefit (like closure encapsulation).
- Improvement Suggestions: Replace the nested functions with a single named method within the class or a simple lambda if the logic remains a single line.
- Priority Level: Low