Code Smell Type: Blocking UI with Sleep
Problem Location: 
  In `add_user` method: `time.sleep(0.3)`
  In `delete_user` method: `time.sleep(0.2)`

Detailed Explanation:
  Using `time.sleep` in GUI event handlers blocks the main thread, freezing the entire application interface for 0.3s and 0.2s respectively. This violates core GUI principles, making the application unresponsive during operations. The artificial delay is a severe design flaw that degrades user experience and should never appear in production code. The sleep is completely unnecessary for the described functionality.

Improvement Suggestions:
  Remove all `time.sleep` calls. If a delay is needed for demonstration purposes, replace with non-blocking operations using `QTimer` (e.g., `QTimer.singleShot(300, self.update_ui)`). For production, eliminate artificial delays entirely as they serve no functional purpose.

Priority Level: High

Code Smell Type: Inconsistent Naming Conventions
Problem Location:
  `self.nameInput`, `self.txtAge`, `self.buttonDelete` (camelCase)
  vs `self.btn_add_user` (snake_case)

Detailed Explanation:
  Python follows PEP8 naming conventions requiring snake_case for variables and functions. The inconsistent use of camelCase (`nameInput`, `txtAge`, `buttonDelete`) versus snake_case (`btn_add_user`) creates visual noise and confusion. This violates team standards and makes the code harder to read/maintain. Example: `txtAge` should be `age_input` to match Python conventions.

Improvement Suggestions:
  Rename all variables to snake_case:
  - `nameInput` → `name_input`
  - `txtAge` → `age_input`
  - `buttonDelete` → `button_delete`
  Maintain consistent naming for all UI elements (e.g., `self.user_input` instead of `self.nameInput`).

Priority Level: Medium

Code Smell Type: Violation of Single Responsibility Principle
Problem Location:
  `add_user` method handles:
  - Input validation
  - Business logic (user creation)
  - UI updates (status/output)
  - Artificial delay (sleep)
  Similarly for `delete_user`

Detailed Explanation:
  Each method performs multiple unrelated tasks (validation, data mutation, UI updates, non-functional delays). This creates tightly coupled code where changes to one concern (e.g., input validation) require touching UI logic. It also prevents unit testing of business logic and makes error handling inconsistent. The sleep further compounds the violation.

Improvement Suggestions:
  1. Extract business logic to a dedicated model class (e.g., `UserManager`).
  2. Keep UI methods minimal (e.g., `on_add_user` calls model, updates UI).
  3. Remove all sleeps – business logic should be synchronous without artificial delays.
  Example refactoring:
  ```python
  # In MainWindow
  def on_add_user(self):
      if not self.name_input.text() or not self.age_input.text():
          self.lblStatus.setText("Missing input")
          return
      self.user_manager.add_user(self.name_input.text(), self.age_input.text())
      self.output.append(f"Added: {name}, {age}")

  # In User model
  class UserManager:
      def add_user(self, name, age):
          # Validation and business logic
          self.users.append({"name": name, "age": age})
  ```

Priority Level: High

Code Smell Type: Fragile State Management
Problem Location:
  `refresh_status` method using string comparisons:
  ```python
  if self.last_action == "add": ...
  elif self.last_action == "delete": ...
  ```

Detailed Explanation:
  Relying on string literals for state management creates fragile code. If the action strings change (e.g., "add" → "created"), the method breaks. It also couples UI state to string values instead of using type-safe mechanisms. The `last_action` state isn't reset after refresh, creating potential for stale state.

Improvement Suggestions:
  Replace string comparisons with type-safe state management:
  ```python
  # Define action types as constants or enum
  ACTION_ADD = "add"
  ACTION_DELETE = "delete"
  
  # In UI methods:
  self.last_action = ACTION_ADD
  # ...
  
  # In refresh_status:
  if self.last_action == ACTION_ADD:
  ```
  Alternatively, remove `last_action` entirely by having UI update directly when actions occur.

Priority Level: Medium

Code Smell Type: Missing Error Handling
Problem Location:
  `add_user` method:
  ```python
  try:
      age = int(age_text)
  except:
      self.lblStatus.setText("Invalid age")
      return
  ```

Detailed Explanation:
  Bare `except` catches all exceptions (including `KeyboardInterrupt`), masking potential bugs. It fails to distinguish between validation errors (e.g., non-integer) and unexpected exceptions. This violates exception handling best practices.

Improvement Suggestions:
  Specify exception types and add meaningful error handling:
  ```python
  try:
      age = int(age_text)
  except ValueError:
      self.lblStatus.setText("Age must be a number")
      return
  ```
  Consider adding specific error messages for user guidance.

Priority Level: Medium