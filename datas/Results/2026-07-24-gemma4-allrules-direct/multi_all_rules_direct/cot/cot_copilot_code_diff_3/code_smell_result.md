- Code Smell Type: Shared Mutable State (Global Variables)
- Problem Location: `globalLabel = None`, `anotherGlobal = "Hello"`, and `global globalLabel` inside `veryStrangeFunctionNameThatDoesTooMuch`.
- Detailed Explanation: The use of global variables to track UI components creates hidden coupling and makes the code difficult to test and reason about. If multiple windows were instantiated, they would all fight over the same global reference, leading to unpredictable behavior.
- Improvement Suggestions: Encapsulate the label as an instance attribute of the `MyWeirdWindow` class (e.g., `self.label`) and pass it as an argument to functions that need to modify it.
- Priority Level: High

- Code Smell Type: Violation of Single Responsibility Principle / Poor Naming
- Problem Location: `def veryStrangeFunctionNameThatDoesTooMuch(window):`
- Detailed Explanation: The function name explicitly admits to doing too much. It handles UI layout creation, widget instantiation, and event logic binding all in one place. This makes the code hard to maintain and prevents the reuse of individual components.
- Improvement Suggestions: Rename the function to something descriptive (e.g., `setup_main_layout`). Better yet, move the layout and widget logic into the `MyWeirdWindow` class methods to follow object-oriented principles.
- Priority Level: Medium

- Code Smell Type: Deeply Nested Conditional/Function Logic
- Problem Location: 
```python
    def inner():
        def inner2():
            lbl.setText("巢狀函式被呼叫")
        inner2()
```
- Detailed Explanation: Defining functions within functions (especially multiple levels deep) increases cognitive load and makes the logic harder to follow without providing any functional benefit in this context.
- Improvement Suggestions: Flatten the logic. Define a single named method within the class to handle the button click event.
- Priority Level: Medium

- Code Smell Type: Redundant Logic / Potential Bug
- Problem Location: 
```python
    btn1.clicked.connect(lambda: lbl.setText("你按了第一個按鈕"))
    btn1.clicked.connect(lambda: lbl.setText("真的按了第一個按鈕"))
```
- Detailed Explanation: `btn1` has two separate lambda functions connected to the same signal. Both will execute sequentially, meaning the first text update will be immediately overwritten by the second, making the first call useless and confusing to the reader.
- Improvement Suggestions: Consolidate the logic into a single function or lambda that performs the intended final action.
- Priority Level: Low