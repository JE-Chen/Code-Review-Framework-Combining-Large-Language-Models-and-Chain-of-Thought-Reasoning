- Code Smell Type: Shared Mutable State (Global Variables)
- Problem Location: `GLOBAL_TEXT = ""`, `GLOBAL_COUNTER = 0`, `GLOBAL_MODE = "default"` and their usage via `global` keywords in `handle_btn1`, `handle_btn2`, and `handle_btn3`.
- Detailed Explanation: The application relies on module-level global variables to maintain state. This introduces hidden coupling and makes the code difficult to test, debug, and scale. If multiple `MainWindow` instances were created, they would all manipulate the same global state, leading to unpredictable behavior.
- Improvement Suggestions: Encapsulate the state within the `MainWindow` class as instance attributes (e.g., `self.text`, `self.counter`, `self.mode`) or create a dedicated State Manager class.
- Priority Level: High

- Code Smell Type: Deeply Nested Conditional Logic
- Problem Location: `handle_btn2` method.
- Detailed Explanation: The method uses nested `if/else` blocks to determine which message to append to the text area. This increases cognitive load and makes the logic harder to follow as more conditions are added.
- Improvement Suggestions: Use guard clauses to handle the "small counter" case early and return. Refactor the mode-based logic into a separate helper method or use a dictionary mapping for different modes.
- Priority Level: Medium

- Code Smell Type: Unclear Naming
- Problem Location: `btn1`, `btn2`, `btn3`, `input1`, `label1`, `handle_btn1`, `handle_btn2`, `handle_btn3`.
- Detailed Explanation: Names like `btn1` and `handle_btn1` are generic and do not describe the purpose or intent of the widgets and their associated logic. This forces the developer to read the implementation details to understand what the button actually does.
- Improvement Suggestions: Rename variables to reflect their function, e.g., `btn_add_text`, `input_text_field`, `handle_add_text_clicked`.
- Priority Level: Medium

- Code Smell Type: Implicit Truthiness / Magic Numbers
- Problem Location: `if len(text) > 0:` and `if GLOBAL_COUNTER > 5:`.
- Detailed Explanation: While `len(text) > 0` is explicit, the number `5` is a "magic number"—a hard-coded constant without a named definition, making it unclear why 5 is the threshold for a "large" counter.
- Improvement Suggestions: Define a named constant at the top of the class or module, such as `COUNTER_THRESHOLD = 5`, to provide semantic meaning to the value.
- Priority Level: Low