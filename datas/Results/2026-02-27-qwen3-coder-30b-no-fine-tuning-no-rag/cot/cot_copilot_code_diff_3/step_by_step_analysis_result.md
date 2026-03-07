1. **Code Smell: Global Variable Assignment**
   - **Issue**: The code modifies a global variable `globalLabel` inside a function without proper encapsulation.
   - **Explanation**: Using global variables can lead to unpredictable behavior, as changes to the variable affect the entire program scope. It's unclear who or what modifies `globalLabel`, making debugging harder.
   - **Impact**: Reduces code maintainability and readability; introduces hidden dependencies.
   - **Fix**: Replace global usage with class attributes or pass values via parameters.
     ```python
     # Instead of:
     global globalLabel
     globalLabel = "some value"

     # Do this:
     self.global_label = "some value"
     ```
   - **Best Practice**: Avoid global state when possible. Prefer dependency injection or class fields for shared data.

2. **Code Smell: Unused Variable**
   - **Issue**: The variable `anotherGlobal` is declared but never used.
   - **Explanation**: Dead code clutters the program and may confuse developers. Unused variables often indicate incomplete refactoring or oversight.
   - **Impact**: Minor impact on readability; no functional risk.
   - **Fix**: Remove the unused variable entirely.
     ```python
     # Remove this line:
     anotherGlobal = "Hello"
     ```
   - **Best Practice**: Regularly clean up dead code during development to keep projects lean and readable.

3. **Code Smell: Function Name Does Not Reflect Behavior**
   - **Issue**: The function name `veryStrangeFunctionNameThatDoesTooMuch` doesn't clearly explain its role.
   - **Explanation**: Poor naming makes it hard for others (or future you) to understand what the function does at a glance.
   - **Impact**: Lowers maintainability and increases cognitive load.
   - **Fix**: Rename the function to accurately describe its responsibilities.
     ```python
     # Before:
     def veryStrangeFunctionNameThatDoesTooMuch():

     # After:
     def setup_main_window():
     ```
   - **Best Practice**: Use descriptive function names that express intent. Follow the principle of “what it does” rather than “how it does it.”

4. **Code Smell: Duplicate Event Handlers**
   - **Issue**: Two lambda expressions assign different text to the same label upon clicking `btn1`.
   - **Explanation**: The second lambda overwrites the first one, leading to confusing behavior. This pattern suggests poor design — mixing unrelated actions under one event.
   - **Impact**: Confusion for developers and potential runtime inconsistencies.
   - **Fix**: Consolidate actions into a single meaningful handler.
     ```python
     # Instead of:
     btn1.clicked.connect(lambda: lbl.setText("你按了第一個按鈕"))
     btn1.clicked.connect(lambda: lbl.setText("真的按了第一個按鈕"))

     # Do:
     btn1.clicked.connect(lambda: lbl.setText("真的按了第一個按鈕"))
     ```
   - **Best Practice**: Each event handler should perform one logical action. Avoid duplicating logic in event connections.

5. **Code Smell: Nested Functions**
   - **Issue**: A nested function `inner2()` is defined inside another nested function `inner()`.
   - **Explanation**: Deep nesting reduces clarity and makes unit testing more difficult. Nested functions are typically only useful if they’re tightly coupled to their outer function.
   - **Impact**: Makes code harder to read, test, and refactor.
   - **Fix**: Extract nested functions into top-level methods.
     ```python
     # Instead of:
     def outer():
         def inner():
             def inner2():
                 ...

     # Do:
     def inner_function():
         ...
     def outer():
         inner_function()
     ```
   - **Best Practice**: Flatten deeply nested structures for improved readability and testability.

6. **Code Smell: Hardcoded Text Strings**
   - **Issue**: UI strings like `"按我一下"` are hardcoded directly in the code.
   - **Explanation**: Hardcoding strings makes localization and updates challenging. If content needs to change or support multiple languages, it becomes messy.
   - **Impact**: Limits scalability and internationalization efforts.
   - **Fix**: Externalize strings into dictionaries or resource files.
     ```python
     # Example:
     TEXTS = {
         "button1": "按我一下",
         "title": "這是一個奇怪的 GUI"
     }
     lbl.setText(TEXTS["button1"])
     ```
   - **Best Practice**: Use localization frameworks or translation-ready data structures to support multi-language applications.

--- 

These improvements will enhance code quality by promoting cleaner architecture, better maintainability, and easier collaboration among developers.