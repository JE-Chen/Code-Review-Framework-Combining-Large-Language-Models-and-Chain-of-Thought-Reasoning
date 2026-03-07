### 🧪 PR Summary Template
- **Summary**: Added input validation, security checks, and logging enhancements.
- **Impact Scope**: Core logic, helper functions, and external calls.
- **Purpose**: Improve security, readability, and maintainability.
- **Risks**: Potential security exposure in `unsafe_eval`.
- **Confirm Points**: Security risks, helper function clarity, and test coverage.
- **Items to Confirm**: Security review, logging clarity, and test integration.

---

### 📄 Code Diff Review

#### ✅ **1. Input Validation & Security**
- **Issue**: `unsafe_eval` uses `eval`, exposing risk.
- **Fix**: Replace with safer alternatives or sanitization.
- **Fix Example**:
  ```python
  def safe_eval(user_code):
      try:
          return eval(user_code)
      except Exception:
          return "Invalid input"
  ```

#### ✅ **2. Helper Function Clarity**
- **Issue**: `check_value` and `timestamped_message` lack context.
- **Fix**: Add comments and usage examples.
- **Fix Example**:
  ```python
  def check_value(val):
      """Check if value is not empty."""
      return "Has value" if val else "No value"
  ```

#### ✅ **3. Core Logic Refactoring**
- **Issue**: `process_user_input` and `run_task` are tightly coupled.
- **Fix**: Extract shared logic into helper functions.
- **Fix Example**:
  ```python
  def validate_input(user_input):
      if not isinstance(user_input, str):
          raise ValueError("Input must be a string.")
      return user_input
  ```

#### ✅ **4. Logging & Debugging**
- **Issue**: `timestamped_message` is unused.
- **Fix**: Use it for logging or debug assertions.
- **Fix Example**:
  ```python
  def debug_message(msg):
      print(f"{time.time()} - {msg}")
  ```

---

### 📝 Key Feedback
- **Security**: Avoid `eval` and sanitize inputs.
- **Readability**: Add comments for edge cases and helper logic.
- **Test Coverage**: Include tests for helper functions and edge cases.
- **Modularity**: Extract shared logic to reduce coupling.