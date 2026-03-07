### 1. **Global Variable Assignment Not Allowed (`no-global-assign`)**
- **Issue**: You're assigning a value to `GLOBAL_SESSION`, which is a global variable.
- **Explanation**: Modifying global variables directly makes your code harder to test and reason about.
- **Root Cause**: The code assumes `GLOBAL_SESSION` exists globally and modifies it without using dependency injection or parameters.
- **Impact**: Reduces modularity, increases risk of side effects, and complicates unit testing.
- **Fix**: Avoid modifying globals; instead, pass dependencies like sessions as arguments to functions.
  ```python
  # Instead of:
  GLOBAL_SESSION = requests.Session()

  # Do:
  def fetch_data(session):
      return session.get("https://example.com")
  ```
- **Best Practice**: Prefer local scope or injected dependencies over global state.

---

### 2. **Unused Variable Detected (`no-unused-vars`)**
- **Issue**: The variable `ANOTHER_GLOBAL` is declared but never used.
- **Explanation**: Dead code clutters the program and may confuse developers.
- **Root Cause**: Either the variable was meant to be used later or was accidentally created.
- **Impact**: Decreases readability and introduces unnecessary clutter.
- **Fix**: Remove unused variables.
  ```python
  # Before:
  GLOBAL_SESSION = requests.Session()
  ANOTHER_GLOBAL = "https://jsonplaceholder.typicode.com/posts"

  # After:
  GLOBAL_SESSION = requests.Session()
  ```
- **Best Practice**: Regularly clean up unused code during refactoring.

---

### 3. **Function Name Too Long / Unclear Purpose (`function-name`)**
- **Issue**: Function name `functionThatDoesTooMuchAndIsHardToUnderstand` is too vague.
- **Explanation**: A good function name should clearly express what it does.
- **Root Cause**: Violation of Single Responsibility Principle leads to ambiguous naming.
- **Impact**: Makes code harder to understand and maintain.
- **Fix**: Rename the function to reflect one clear task.
  ```python
  # Instead of:
  def functionThatDoesTooMuchAndIsHardToUnderstand():

  # Use:
  def fetch_and_post_sample_data():
  ```
- **Best Practice**: Follow the principle that each function should do only one thing.

---

### 4. **Catching Generic Exception (`no-catch-undefined`)**
- **Issue**: Using `except:` catches all exceptions, hiding potential bugs.
- **Explanation**: It prevents proper error handling and makes debugging difficult.
- **Root Cause**: Lack of specificity in exception handling.
- **Impact**: Can mask real issues, especially in production environments.
- **Fix**: Catch specific exceptions.
  ```python
  # Instead of:
  except Exception as e:
      print("錯誤但我不管:", e)

  # Use:
  except requests.exceptions.RequestException as e:
      logger.error(f"Request failed: {e}")
  ```
- **Best Practice**: Handle known exceptions explicitly and log them appropriately.

---

### 5. **Inconsistent or Non-Descriptive Variable Names (`variable-naming`)**
- **Issue**: Variable name `weirdVariableName` lacks clarity.
- **Explanation**: Descriptive names help readers quickly grasp intent.
- **Root Cause**: Poor naming habits or lack of attention to naming standards.
- **Impact**: Reduces readability and increases cognitive load on developers.
- **Fix**: Use meaningful variable names.
  ```python
  # Instead of:
  weirdVariableName = response.text

  # Use:
  post_response = response.text
  ```
- **Best Practice**: Choose variable names that describe their purpose and content.

---

### 6. **Use of Print Statements in Production Code (`no-console`)**
- **Issue**: Multiple `print()` statements are used for outputting logs.
- **Explanation**: Print statements are not suitable for production due to limited control.
- **Root Cause**: Inadequate logging strategy.
- **Impact**: Makes deployment harder and less flexible for monitoring and debugging.
- **Fix**: Replace `print()` with Python’s `logging` module.
  ```python
  import logging
  logging.info("Data fetched successfully")
  ```
- **Best Practice**: Always use structured logging for production systems.

---

### 7. **Hardcoded URLs (`Magic Strings`)**
- **Issue**: URLs are hardcoded throughout the code.
- **Explanation**: Makes future updates harder and reduces reusability.
- **Root Cause**: Lack of abstraction for configuration values.
- **Impact**: Increases maintenance cost and error-proneness.
- **Fix**: Define constants for URLs.
  ```python
  BASE_URL = "https://jsonplaceholder.typicode.com"
  POST_ENDPOINT = f"{BASE_URL}/posts"
  POST_DETAIL_ENDPOINT = f"{BASE_URL}/posts/1"
  ```
- **Best Practice**: Extract static values into constants or config files.

---

### 8. **God Function / Function That Does Too Much**
- **Issue**: One function handles fetching, posting, printing, and error handling.
- **Explanation**: Violates the Single Responsibility Principle (SRP).
- **Root Cause**: Overloading a single function with too many tasks.
- **Impact**: Difficult to test, debug, and extend.
- **Fix**: Break it down into smaller, focused functions.
  ```python
  def fetch_post_details():
      ...

  def send_post_request():
      ...

  def log_results():
      ...
  ```
- **Best Practice**: Each function should have one clear responsibility.

---

### 9. **Lack of Input Validation (Security Risk)**
- **Issue**: No validation or sanitization of inputs.
- **Explanation**: Sending raw data without checks can lead to vulnerabilities.
- **Impact**: Potential security risks in real-world applications.
- **Fix**: Add input validation where necessary.
  ```python
  if isinstance(data, dict):
      # Proceed with safe handling
  else:
      raise ValueError("Invalid input format")
  ```
- **Best Practice**: Validate and sanitize all external inputs.

---

### 10. **No Return Values or State Management**
- **Issue**: Function has no return statement, limiting reusability.
- **Explanation**: Side-effect-only functions are hard to integrate into larger systems.
- **Impact**: Limits composability and testing capabilities.
- **Fix**: Make functions return useful data.
  ```python
  def get_post_data():
      response = session.get(url)
      return response.json()
  ```
- **Best Practice**: Functions should either return something meaningful or be designed for side effects alone.

---

### 11. **Missing Documentation and Comments**
- **Issue**: No docstrings or inline comments.
- **Explanation**: Without explanation, even good names become ambiguous.
- **Impact**: Hinders collaboration and future maintenance.
- **Fix**: Add docstrings and comments for clarity.
  ```python
  def fetch_and_post_sample_data():
      """
      Fetches a sample post and posts a new one.
      Returns:
          dict: The updated post data.
      """
  ```
- **Best Practice**: Document everything—functions, modules, and complex logic.

--- 

### Summary Table

| Issue | Description | Fix | Best Practice |
|-------|-------------|-----|----------------|
| 1 | Global assignment forbidden | Pass session as parameter | Avoid global state |
| 2 | Unused variable | Delete unused var | Clean dead code |
| 3 | Unclear function name | Rename to reflect action | SRP + descriptive naming |
| 4 | Catch-all exceptions | Catch specific exceptions | Specific error handling |
| 5 | Vague variable names | Use descriptive names | Meaningful identifiers |
| 6 | Print statements in prod | Use logging | Structured logging |
| 7 | Hardcoded URLs | Define constants | Configuration abstraction |
| 8 | God function | Split into small functions | SRP |
| 9 | Missing input validation | Add checks | Secure coding practices |
| 10 | No return values | Return structured data | Functional design |
| 11 | No docs/comments | Add docstrings/comments | Code clarity |

By addressing these points, you'll improve code quality, readability, and maintainability while reducing technical debt.