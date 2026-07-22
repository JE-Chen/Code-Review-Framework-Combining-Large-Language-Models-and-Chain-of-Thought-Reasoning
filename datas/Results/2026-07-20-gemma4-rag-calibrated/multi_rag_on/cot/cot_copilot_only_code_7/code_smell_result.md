- Code Smell Type: Shared Mutable State (Global Variables)
- Problem Location: 
  ```python
  GLOBAL_TEXT = ""
  GLOBAL_COUNTER = 0
  GLOBAL_MODE = "default"
  # and subsequent 'global' declarations in handle_btn1, handle_btn2, handle_btn3
  ```
- Detailed Explanation: The application relies on module-level global variables to maintain state. This introduces hidden coupling and makes the code difficult to test, as the state persists across different instances of `MainWindow` or test cases. It violates the principle of encapsulation and makes the data flow opaque, as any function in the module can mutate these values.
- Improvement Suggestions: Move `GLOBAL_TEXT`, `GLOBAL_COUNTER`, and `GLOBAL_MODE` into the `MainWindow` class as instance attributes (e.g., `self.text`, `self.counter`, `self.mode`) initialized in the `__init__` method.
- Priority Level: High

- Code Smell Type: Unclear Naming
- Problem Location: 
  ```python
  self.btn1, self.btn2, self.btn3, self.input1, self.label1
  self.handle_btn1, self.handle_btn2, self.handle_btn3
  ```
- Detailed Explanation: The names are generic and based on the order of creation rather than the purpose of the widgets. This forces a developer to read the button labels or the implementation logic to understand what `btn2` or `handle_btn2` actually does, reducing maintainability and readability.
- Improvement Suggestions: Rename variables to reflect their semantic purpose. For example:
  - `btn1` $\rightarrow$ `add_text_button` / `handle_btn1` $\rightarrow$ `on_add_text_clicked`
  - `btn2` $\rightarrow$ `show_counter_button` / `handle_btn2` $\rightarrow$ `on_show_counter_clicked`
  - `btn3` $\rightarrow$ `reset_button` / `handle_btn3` $\rightarrow$ `on_reset_clicked`
  - `input1` $\rightarrow$ `text_input`
  - `label1` $\rightarrow$ `status_label`
- Priority Level: Medium

- Code Smell Type: Deeply Nested Logic (Arrow Anti-pattern)
- Problem Location: 
  ```python
  def handle_btn2(self):
      if GLOBAL_COUNTER > 5:
          if GLOBAL_MODE == "default":
              # ...
          else:
              if GLOBAL_COUNTER % 2 == 0:
                  # ...
              else:
                  # ...
  ```
- Detailed Explanation: The `handle_btn2` method contains multiple levels of nested `if/else` statements. This increases cognitive load and makes the logic harder to follow and modify.
- Improvement Suggestions: Use guard clauses to flatten the logic. Handle the "small counter" case first and return early, or use a more structured approach to determine the message string before calling `self.textArea.append()`.
- Priority Level: Low