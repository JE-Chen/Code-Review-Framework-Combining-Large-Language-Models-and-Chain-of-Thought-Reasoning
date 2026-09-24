- Code Smell Type: SQL Injection Vulnerability
- Problem Location: 
  - `setup()`: `f"INSERT INTO logs (msg, ts) VALUES ('init-{i}', {time.time()})"`
  - `write_log(message)`: `sql = f"INSERT INTO logs (msg, ts) VALUES ('{message}', {time.time()})"`
  - `read_logs(limit)`: `base += " LIMIT " + str(limit)`
- Detailed Explanation: The code uses Python f-strings and string concatenation to build SQL queries. This is a critical security flaw. If the `message` or `limit` parameters were to come from user input, an attacker could inject malicious SQL commands to delete data, bypass authentication, or leak sensitive information. Even in internal apps, this leads to crashes if a message contains a single quote (e.g., `"User's login"`).
- Improvement Suggestions: Use **parameterized queries** (prepared statements). Replace f-strings with `?` placeholders and pass the values as a tuple to the `execute` method.
  - Example: `CURSOR.execute("INSERT INTO logs (msg, ts) VALUES (?, ?)", (message, time.time()))`
- Priority Level: High

---

- Code Smell Type: Unreliable Transaction Management (Non-Deterministic Commits)
- Problem Location: `write_log(message)`: `if random.choice([True, False]): CONN.commit()`
- Detailed Explanation: Committing data based on a random boolean is highly dangerous. It creates a state where data is written to the cursor but not persisted to the database unpredictably. This leads to "lost updates" and makes the system impossible to debug or rely upon for data integrity.
- Improvement Suggestions: Remove the random condition. Commit transactions based on logical units of work (e.g., at the end of a business operation) or use a context manager (`with CONN:`) to ensure atomic transactions.
- Priority Level: High

---

- Code Smell Type: Silent Exception Swallowing
- Problem Location: `do_business_logic_but_sql_heavy()`: `except Exception: pass`
- Detailed Explanation: Catching the base `Exception` class and doing nothing (`pass`) is a major anti-pattern. It hides critical failures (like disk full, database corruption, or connection loss), making it impossible to detect when the application is failing.
- Improvement Suggestions: Remove the empty `try-except` block. If specific errors are expected, catch only those specific exceptions and log them using a logging framework.
- Priority Level: Medium

---

- Code Smell Type: Global State / Tight Coupling
- Problem Location: `CONN = sqlite3.connect(":memory:")` and `CURSOR = CONN.cursor()`
- Detailed Explanation: The database connection and cursor are defined as global variables. This makes the code difficult to test (unit tests will share the same state), prevents the app from scaling to multiple database connections, and creates tight coupling between the functions and a specific global instance.
- Improvement Suggestions: Use a dependency injection pattern. Pass the `connection` or `cursor` as an argument to the functions, or wrap the database logic in a Class (e.g., `LogDatabase`) that manages its own connection lifecycle.
- Priority Level: Medium