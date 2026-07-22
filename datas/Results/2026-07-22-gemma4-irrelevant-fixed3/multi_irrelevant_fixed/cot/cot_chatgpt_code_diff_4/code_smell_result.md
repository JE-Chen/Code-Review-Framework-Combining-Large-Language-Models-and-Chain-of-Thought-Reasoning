- Code Smell Type: SQL Injection Vulnerability
- Problem Location: 
  - `setup()`: `f"INSERT INTO logs (msg, ts) VALUES ('init-{i}', {time.time()})"`
  - `write_log(message)`: `sql = f"INSERT INTO logs (msg, ts) VALUES ('{message}', {time.time()})"`
  - `read_logs(limit)`: `base += " LIMIT " + str(limit)`
- Detailed Explanation: The code uses Python f-strings and string concatenation to build SQL queries. This is a critical security flaw. If `message` or `limit` were to come from user input, an attacker could execute arbitrary SQL commands (SQL Injection), potentially leading to data theft or database destruction.
- Improvement Suggestions: Use parameterized queries (prepared statements). Replace f-strings with `?` placeholders and pass values as a tuple to the `execute` method.
  - Example: `CURSOR.execute("INSERT INTO logs (msg, ts) VALUES (?, ?)", (message, time.time()))`
- Priority Level: High

- Code Smell Type: Unreliable Data Persistence (Non-Deterministic Commits)
- Problem Location: `write_log(message)`: `if random.choice([True, False]): CONN.commit()`
- Detailed Explanation: Committing transactions based on a random boolean is logically incorrect. This leads to non-deterministic behavior where some logs are persisted and others are lost if the application crashes or closes, making the system unpredictable and impossible to debug.
- Improvement Suggestions: Remove the random condition. Commit transactions based on a defined business boundary (e.g., at the end of a logical unit of work) or use a context manager for transactions.
- Priority Level: High

- Code Smell Type: Silent Exception Swallowing
- Problem Location: `do_business_logic_but_sql_heavy()`: `except Exception: pass`
- Detailed Explanation: Catching the base `Exception` class and doing nothing (`pass`) hides critical failures. If a database constraint is violated or the connection is lost, the developer will never know why the operation failed, leading to "silent failures" that are extremely difficult to troubleshoot.
- Improvement Suggestions: Catch specific exceptions (e.g., `sqlite3.Error`) and implement proper logging or error propagation so the failure can be handled or audited.
- Priority Level: Medium

- Code Smell Type: Global State / Tight Coupling
- Problem Location: `CONN = sqlite3.connect(":memory:")` and `CURSOR = CONN.cursor()`
- Detailed Explanation: The database connection and cursor are defined as global variables. This makes the code difficult to test (unit tests will share state), prevents the app from handling multiple database connections, and is not thread-safe.
- Improvement Suggestions: Encapsulate the database logic into a class (e.g., `LogDatabase`) or pass the connection/cursor as arguments to the functions.
- Priority Level: Medium