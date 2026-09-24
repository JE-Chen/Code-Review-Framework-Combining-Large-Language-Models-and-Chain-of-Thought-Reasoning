### Code Smell Type: SQL Injection Vulnerability
- **Problem Location**:
  ```python
  def write_log(message):
      sql = f"INSERT INTO logs (msg, ts) VALUES ('{message}', {time.time()})"
      CURSOR.execute(sql)
  ```
- **Detailed Explanation**:  
  The `message` parameter is directly interpolated into the SQL string without sanitization. This creates a critical security risk where malicious input could inject arbitrary SQL commands (e.g., `message = "'); DROP TABLE logs; --"`). Even though the current usage restricts messages to a fixed set, the function's design violates fundamental security principles and could lead to catastrophic data loss in production. This is a severe violation of input validation best practices.
- **Improvement Suggestions**:  
  Replace string interpolation with parameterized queries:
  ```python
  CURSOR.execute("INSERT INTO logs (msg, ts) VALUES (?, ?)", (message, time.time()))
  ```
  This ensures all user input is treated as data, not executable code.
- **Priority Level**: High

---

### Code Smell Type: Global State Usage
- **Problem Location**:
  ```python
  CONN = sqlite3.connect(":memory:")
  CURSOR = CONN.cursor()
  ```
  Used throughout all functions (`setup()`, `write_log()`, `read_logs()`, etc.).
- **Detailed Explanation**:  
  Global variables `CONN` and `CURSOR` create tight coupling, making the code impossible to test in isolation (e.g., mocking database operations). Changes to these globals can cause unexpected side effects. This violates encapsulation and the single responsibility principle, as the database connection is managed outside any logical context.
- **Improvement Suggestions**:  
  Encapsulate database operations in a class with dependency injection:
  ```python
  class Logger:
      def __init__(self, conn):
          self.conn = conn
          self.cursor = conn.cursor()
      
      def write(self, message):
          self.cursor.execute("INSERT INTO logs (msg, ts) VALUES (?, ?)", (message, time.time()))
          if random.choice([True, False]):
              self.conn.commit()
  ```
  Pass the connection as a dependency to `Logger`.
- **Priority Level**: High

---

### Code Smell Type: Non-Deterministic Transaction Management
- **Problem Location**:
  ```python
  if random.choice([True, False]):
      CONN.commit()
  ```
  (in `write_log`) and
  ```python
  try:
      CONN.commit()
  except Exception:
      pass
  ```
  (in `do_business_logic_but_sql_heavy`)
- **Detailed Explanation**:  
  The decision to commit transactions is randomized, leading to inconsistent data state. This could cause:
  - Data loss if the transaction isn't committed.
  - Duplicates if the same log is written multiple times.
  - Inability to reproduce bugs due to non-determinism.
  The final `commit()` in `do_business_logic_but_sql_heavy` is redundant and error-prone (broad `except` swallows all exceptions).
- **Improvement Suggestions**:  
  Remove randomness and manage transactions explicitly:
  1. Let the caller control transaction boundaries.
  2. Replace `try/except` with specific exception handling.
  3. Use context managers for transaction safety.
  Example:
  ```python
  def write_log(self, message):
      self.cursor.execute("INSERT INTO logs (msg, ts) VALUES (?, ?)", (message, time.time()))
      # Never commit here; let caller decide
  ```
- **Priority Level**: High

---

### Code Smell Type: Unclear Naming & Poor Abstraction
- **Problem Location**:
  ```python
  def do_business_logic_but_sql_heavy():
  ```
  and
  ```python
  random.choice([
      "user_login",
      "user_logout",
      "something_happened",
      "???"
  ])
  ```
- **Detailed Explanation**:  
  The function name is unprofessional ("but_sql_heavy" is negative and uninformative). The hardcoded messages ("???") lack clarity and are prone to future confusion. The function mixes multiple responsibilities (log generation, reading logs, transaction management), violating the single responsibility principle. This makes the code hard to understand, test, and maintain.
- **Improvement Suggestions**:  
  Rename function descriptively and split concerns:
  ```python
  def simulate_user_activity(logger: Logger, log_limit: int = None) -> list:
      for _ in range(random.randint(1, 5)):
          logger.write(random.choice(["user_login", "user_logout", "something_happened"]))
      return logger.read(limit=log_limit)
  ```
  Define message constants:
  ```python
  LOG_EVENTS = ["user_login", "user_logout", "something_happened"]
  ```
- **Priority Level**: Medium

---

### Code Smell Type: Inconsistent Parameter Handling
- **Problem Location**:
  ```python
  if limit:
      base += " LIMIT " + str(limit)
  ```
  (in `read_logs`)
- **Detailed Explanation**:  
  The `limit` parameter is silently converted to a string without validation. If `limit` is non-integer (e.g., `None`, string, negative number), the SQL query becomes invalid. The function also lacks documentation for parameter expectations, increasing the risk of misuse.
- **Improvement Suggestions**:  
  Validate parameters and add docstrings:
  ```python
  def read_logs(limit: int = None) -> list:
      """
      Fetch logs with optional limit.
      
      Args:
          limit: Maximum number of logs to return (int, optional).
      
      Returns:
          List of formatted log strings.
      """
      if limit is not None and not isinstance(limit, int) or limit < 0:
          raise ValueError("limit must be a non-negative integer")
      base = "SELECT id, msg, ts FROM logs ORDER BY ts DESC"
      if limit:
          base += f" LIMIT {limit}"
      return [f"[{int(ts)}] ({i}) {msg}" for i, msg, ts in CURSOR.execute(base).fetchall()]
  ```
- **Priority Level**: Medium