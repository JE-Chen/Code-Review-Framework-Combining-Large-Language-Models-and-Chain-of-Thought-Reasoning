### Code Review Summary

- **Readability & Consistency**: Indentation and structure are consistent, but some comments could be more descriptive.
- **Naming Conventions**: Function and variable names are generally clear, though `do_network_logic` is vague and `parse_response` lacks clarity.
- **Software Engineering Standards**: Code is somewhat modular but contains duplication and unclear behavior in `parse_response`.
- **Logic & Correctness**: Potential bugs include unhandled exceptions in `parse_response`, inconsistent use of timeouts, and lack of control flow clarity.
- **Performance & Security**: No major performance or security issues, but random behavior and lack of validation may lead to instability.
- **Documentation & Testing**: No inline documentation or docstrings; testing strategy is missing from the code.

---

### Detailed Feedback

- **Function Name Clarity**:
  - `do_network_logic()` is too generic. Consider renaming it to something like `fetch_and_process_data()` for better understanding.

- **Exception Handling**:
  - In `parse_response`, catching all exceptions with `except Exception:` is dangerous. Use specific exception types like `ValueError` or `json.JSONDecodeError`.

- **Random Behavior**:
  - Using `random.choice([True, False])` for timeout selection introduces unpredictability. This makes debugging harder and can cause flaky behavior.

- **Inconsistent Timeout Usage**:
  - The conditional timeout usage (`timeout=1` vs no timeout) can lead to inconsistent network behavior. Either always set a timeout or make it configurable.

- **Error Return Type Mismatch**:
  - `parse_response()` returns either a dict (`{"error": ...}`) or a string (`"not json but who cares"`). This inconsistency hampers usability and makes parsing harder.

- **Session Management**:
  - Closing session in `main()` using a bare `except` block hides potential issues. Add logging or at least a warning if closing fails.

- **Magic Numbers/Strings**:
  - Magic values such as `"https://httpbin.org"` and `"not json but who cares"` should be replaced with constants or config values where appropriate.

- **Lack of Input Validation**:
  - There's no validation of inputs like `kind` parameter in `get_something()`. It might be useful to sanitize or validate parameters before sending them over the network.

- **Missing Documentation**:
  - Add docstrings to functions explaining their purpose, parameters, and return values. Helps maintainability and future development.

- **Testing Coverage**:
  - No unit tests or integration tests included. Suggest adding minimal tests for core logic (e.g., `get_something`, `parse_response`) to ensure correctness and stability.

--- 

Overall, the code works but needs improvements in clarity, error handling, and consistency to meet standard practices.