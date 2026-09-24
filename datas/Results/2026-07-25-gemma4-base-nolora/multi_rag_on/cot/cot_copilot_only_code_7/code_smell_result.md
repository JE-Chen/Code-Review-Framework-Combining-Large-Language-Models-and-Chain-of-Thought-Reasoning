- Code Smell Type: Shared Mutable State (Global Variables)
- Problem Location: 
  ```python
  GLOBAL_TEXT = ""
  GLOBAL_COUNTER = 0
  GLOBAL_MODE = "default"
  # And subsequent 'global' declarations in handle_btn1, handle_btn2, handle_btn3
  ```
- Detailed Explanation: The application relies on module-level global variables to maintain state. This introduces hidden coupling between the `MainWindow` class and the global scope. It makes the code difficult to test (as state persists between test cases), prevents the possibility of running multiple `MainWindow` instances independently, and increases the risk of side-effect bugs as the application grows.
- Improvement Suggestions: Encapsulate these variables as instance attributes within the `MainWindow` class (e.g., `self.text`, `self.counter`, `self.mode`) or move them into a dedicated `AppState` data class that is passed to the window.
- Priority Level: High

- Code Smell Type: Unclear Naming
- Problem Location: 
  ```python
  self.btn1, self.btn2, self.btn3, self.input1, self.label1
  self.handle_btn1, self.handle_btn2, self.handle_btn3
  ```
- Detailed Explanation: The naming convention used for UI elements and their handlers is generic and non-descriptive. `btn1` and `handle_btn1` provide no semantic information about the component's purpose. This forces a developer to read the implementation details of the function to understand what the button actually does, hindering maintainability and readability.
- Improvement Suggestions: Rename variables and methods to reflect their intent. For example:
    - `btn1` $\rightarrow$ `add_text_button` / `handle_btn1` $\rightarrow$ `on_add_text_clicked`
    - `btn2` $\rightarrow$ `show_counter_button` / `handle_btn2` $\rightarrow$ `on_show_counter_clicked`
    - `btn3` $\rightarrow$ `reset_button` / `handle_btn3` $\rightarrow$ `on_reset_clicked`
    - `input1` $\rightarrow$ `text_input`
- Priority Level: Medium

- Code Smell Type: Deeply Nested Conditional Logic (Arrow Anti-pattern)
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
- Detailed Explanation: The `handle_btn2` method contains nested `if/else` blocks three levels deep. This increases cognitive load and makes the logic harder to follow. As more modes or conditions are added, this structure will become exponentially more difficult to maintain.
- Improvement Suggestions: Use "Guard Clauses" to return early or flatten the logic. For example, handle the `GLOBAL_COUNTER <= 5` case first and return, then handle the `GLOBAL_MODE` logic.
- Priority Level: Low