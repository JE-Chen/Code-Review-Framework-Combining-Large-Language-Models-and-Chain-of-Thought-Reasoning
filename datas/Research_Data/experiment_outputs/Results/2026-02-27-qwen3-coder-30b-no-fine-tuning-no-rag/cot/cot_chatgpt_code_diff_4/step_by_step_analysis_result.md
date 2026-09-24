### 1. **Global Variable Assignment (`no-global-assign`)**
- **Issue:**  
  The code reassigns global variables `CONN` and `CURSOR`. Global variables should not be modified outside their initialization because it introduces hidden dependencies and makes testing harder.
- **Root Cause:**  
  The code directly assigns database connection and cursor objects to global variables, violating encapsulation and modularity principles.
- **Impact:**  
  This can lead to unpredictable behavior, especially in concurrent environments or when the module is reused. It also makes unit testing difficult since external state is involved.
- **Fix Suggestion:**  
  Move `CONN` and `CURSOR` into a class or function scope, or create a dedicated database manager class.
  ```python
  class DatabaseManager:
      def __init__(self):
          self.conn = sqlite3.connect(":memory:")
          self.cursor = self.conn.cursor()
  ```
- **Best Practice:**  
  Avoid modifying global state; prefer dependency injection or encapsulation through classes.

---

### 2. **Unused Variable (`no-unused-vars`)**
- **Issue:**  
  The loop variable `i` is defined but never used inside the loop body.
- **Root Cause:**  
  Likely a leftover from previous code or an oversight during development.
- **Impact:**  
  Reduces readability and may confuse developers who see unused code.
- **Fix Suggestion:**  
  Remove the unused variable or use it in the loop if intentional.
  ```python
  for _ in range(3):  # Use underscore to indicate unused variable
      ...
  ```
- **Best Practice:**  
  Always remove unused variables unless they're intentionally left for clarity (e.g., `_` for unused).

---

### 3. **Unsafe Negation (`no-unsafe-negation`)**
- **Issue:**  
  Using `if limit:` assumes that `limit` being falsy means it's `None`. However, `0`, `False`, or empty containers are also falsy.
- **Root Cause:**  
  Ambiguous logic due to Python's truthiness rules, which can lead to incorrect behavior.
- **Impact:**  
  Can cause bugs where valid numeric values like `0` are treated as `None`.
- **Fix Suggestion:**  
  Be explicit about checking for `None`.
  ```python
  if limit is not None:
      ...
  ```
- **Best Practice:**  
  Use explicit comparisons (`is None`, `is not None`) when checking for `None`.

---

### 4. **Implicit Type Coercion (`no-implicit-coercion`)**
- **Issue:**  
  Mixing strings and integers in list comprehensions causes implicit conversion, which is unclear and error-prone.
- **Root Cause:**  
  Lack of type awareness in concatenation or formatting operations.
- **Impact:**  
  May introduce subtle bugs or inconsistent output depending on runtime values.
- **Fix Suggestion:**  
  Explicitly cast types using `str()` to ensure clarity.
  ```python
  [f"Log entry {str(i)}" for i in range(10)]
  ```
- **Best Practice:**  
  Prefer explicit type conversion over implicit coercion.

---

### 5. **Empty Block (`no-empty-block`)**
- **Issue:**  
  An empty `except` block exists with no action taken on exception.
- **Root Cause:**  
  Silently ignoring errors prevents proper diagnostics and debugging.
- **Impact:**  
  Can hide serious issues, making troubleshooting harder and potentially masking critical failures.
- **Fix Suggestion:**  
  Handle or log the exception appropriately.
  ```python
  try:
      CONN.commit()
  except Exception as e:
      print(f"Commit failed: {e}")
      raise
  ```
- **Best Practice:**  
  Never silently ignore exceptions—log or handle them meaningfully.

---

### 6. **Duplicate Key (`no-duplicate-key`)**
- **Issue:**  
  A dictionary has duplicate keys, likely causing one value to overwrite another unintentionally.
- **Root Cause:**  
  Misconfiguration or copy-paste error in dictionary construction.
- **Impact:**  
  Unexpected behavior or loss of expected data due to overwriting.
- **Fix Suggestion:**  
  Ensure uniqueness of keys in dictionaries.
  ```python
  data = {"key1": "value1", "key2": "value2"}  # No duplicates
  ```
- **Best Practice:**  
  Validate structures like dictionaries to prevent accidental duplication.

---

### 7. **Hardcoded URL (`no-hardcoded-urls`)**
- **Issue:**  
  The in-memory SQLite connection string `":memory:"` is hardcoded.
- **Root Cause:**  
  Configuration values are embedded directly in code rather than abstracted.
- **Impact:**  
  Makes deployment less flexible and harder to adapt across environments.
- **Fix Suggestion:**  
  Move the connection string to an environment variable or config file.
  ```python
  import os
  db_path = os.getenv("DATABASE_URL", ":memory:")
  CONN = sqlite3.connect(db_path)
  ```
- **Best Practice:**  
  Externalize configurations so applications can be easily adapted to different environments.

---

### 8. **Multiline SQL Formatting (`no-unexpected-multiline`)**
- **Issue:**  
  Multiline SQL queries lack consistent formatting, reducing readability.
- **Root Cause:**  
  Lack of standard formatting practices in SQL string construction.
- **Impact:**  
  Harder to read and debug complex queries.
- **Fix Suggestion:**  
  Format SQL queries clearly with indentation and alignment.
  ```python
  sql = """
      INSERT INTO logs (msg, ts)
      VALUES (?, ?)
  """
  ```
- **Best Practice:**  
  Use triple quotes and proper indentation for multi-line SQL for better readability and maintainability.