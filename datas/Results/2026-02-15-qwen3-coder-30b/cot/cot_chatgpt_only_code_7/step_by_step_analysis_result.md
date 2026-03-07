1. **Unused Variable (`no-unused-vars`)**
   - **Issue**: The variable `txtAge` is declared but never used.
   - **Cause**: Likely leftover from previous development or copy-paste error.
   - **Impact**: Minor code bloat; reduces clarity.
   - **Fix**: Remove unused variable or assign it to an actual purpose.
     ```python
     # Before
     txtAge = self.txtAge.text()
     ...
     # After
     name = self.nameInput.text()
     ```

2. **Implicit Any Type (`no-implicit-any`)**
   - **Issue**: Function lacks explicit typing for parameters or return value.
   - **Cause**: Missing type hints in function signatures.
   - **Impact**: Reduces readability and IDE support; harder to catch type-related bugs.
   - **Fix**: Add explicit types.
     ```python
     def add_user(name: str, age: int) -> bool:
         ...
     ```

3. **Magic Number (`no-magic-numbers`)**
   - **Issue**: Hardcoded value `1000` used as interval delay.
   - **Cause**: Lack of abstraction for time-based constants.
   - **Impact**: Difficult to adjust or document intervals later.
   - **Fix**: Define named constant.
     ```python
     UPDATE_INTERVAL_MS = 1000
     QTimer.singleShot(UPDATE_INTERVAL_MS, ...)
     ```

4. **Duplicate Code (`no-duplicate-code`)**
   - **Issue**: Similar logic exists in `add_user` and `delete_user`.
   - **Cause**: No shared helper function for common actions.
   - **Impact**: Increases chance of inconsistency and maintenance burden.
   - **Fix**: Extract repeated logic into a shared method.
     ```python
     def update_ui_status(message):
         self.lblStatus.setText(message)
         self.lblStatus.setStyleSheet(...)
     ```

5. **Global State (`no-global-state`)**
   - **Issue**: App instance initialized globally at module level.
   - **Cause**: Tight coupling between setup and usage.
   - **Impact**: Makes unit tests harder and reduces reusability.
   - **Fix**: Inject dependencies or encapsulate creation.
     ```python
     app = QApplication(sys.argv)
     window = MainWindow(app)
     ```

6. **Bare Exception Catch (`no-unhandled-exceptions`)**
   - **Issue**: Catches all exceptions without handling specifics.
   - **Cause**: Poor exception management.
   - **Impact**: Masks real problems, hinders debugging.
   - **Fix**: Catch specific exceptions.
     ```python
     try:
         age = int(age_text)
     except ValueError:
         self.lblStatus.setText("Invalid age")
         return
     ```

7. **Side Effects in Core Logic (`no-side-effects`)**
   - **Issue**: Blocking operations (`sleep`) affect UI responsiveness.
   - **Cause**: Mixing async behavior with synchronous code flow.
   - **Impact**: Poor UX and scalability.
   - **Fix**: Offload blocking tasks to background threads.
     ```python
     QTimer.singleShot(300, lambda: self.output.append(...))
     ```

8. **Hardcoded Strings (`Magic Strings`)**
   - **Issue**: Repeated UI messages scattered throughout code.
   - **Cause**: Lack of centralization or localization support.
   - **Impact**: Harder to update or translate UI text.
   - **Fix**: Centralize status messages.
     ```python
     STATUS_MESSAGES = {
         "missing_input": "Missing input",
         "invalid_age": "Invalid age"
     }
     ```

9. **Tight Coupling (`Tight Coupling`)**
   - **Issue**: Direct access to UI elements inside business logic.
   - **Cause**: Mixing concerns and violating separation of layers.
   - **Impact**: Reduced testability and modularity.
   - **Fix**: Introduce a model or service layer.
     ```python
     class UserManager:
         def add_user(self, name, age):
             ...
     ```

10. **Poor Input Validation**
    - **Issue**: Only basic validation performed on inputs.
    - **Cause**: Missing checks for edge cases.
    - **Impact**: Risk of inconsistent or malicious input.
    - **Fix**: Sanitize and validate thoroughly.
      ```python
      if not name.strip() or len(name) > 50:
          self.lblStatus.setText("Invalid name")
      ```

11. **Fixed Geometry (`Hardcoded Geometry`)**
    - **Issue**: Window size is hardcoded.
    - **Cause**: Not using layouts or adaptive sizing.
    - **Impact**: Poor portability and responsiveness.
    - **Fix**: Use layout managers.
      ```python
      self.resize(500, 400)  # Prefer dynamic sizing
      ```

12. **Redundant Status Updates**
    - **Issue**: Same visual styling applied repeatedly.
    - **Cause**: Lack of abstraction for styling.
    - **Impact**: Maintenance overhead.
    - **Fix**: Encapsulate styling logic.
      ```python
      def set_status_color(color):
          self.lblStatus.setStyleSheet(f"color: {color}")
      ```