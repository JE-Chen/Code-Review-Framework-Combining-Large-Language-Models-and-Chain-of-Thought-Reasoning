- Code Smell Type: SQL Injection Vulnerability
- Problem Location: 
  - `setup()`: `f"INSERT INTO logs (msg, ts) VALUES ('init-{i}', {time.time()})"`
  - `write_log(message)`: `sql = f"INSERT INTO logs (msg, ts) VALUES ('{message}', {time.time()})"`
  - `read_logs(limit)`: `base += " LIMIT " + str(limit)`
- Detailed Explanation: The code uses f-strings and string concatenation to build SQL queries. This is a critical security risk. If `message` or `limit` were to come from an external user, they could inject malicious SQL commands to leak data or destroy the database. Even in internal tools, this leads to bugs if a message contains a single quote (e.g., "User's login").
- Improvement Suggestions: Use parameterized queries (prepared statements). Replace f-strings with `?` placeholders and pass values as a tuple to the `execute` method.
  - Example: `CURSOR.execute("INSERT INTO logs (msg, ts) VALUES (?, ?)", (message, time.time()))`
- Priority Level: High

- Code Smell Type: Shared Mutable State (Global Variables)
- Problem Location: `CONN = sqlite3.connect(":memory:")` and `CURSOR = CONN.cursor()`
- Detailed Explanation: The database connection and cursor are defined as global variables. This creates hidden coupling across all functions, making the code difficult to test in isolation and impossible to use in a multi-threaded environment without causing race conditions or crashes.
- Improvement Suggestions: Encapsulate the database logic into a class (e.g., `LogDatabase`) or pass the connection/cursor as an explicit argument to the functions that need them.
- Priority Level: High

- Code Smell Type: Broad Exception Handling
- Problem Location: `do_business_logic_but_sql_heavy()`: `except Exception: pass`
- Detailed Explanation: Catching the base `Exception` class and silencing it with `pass` hides all potential errors (including syntax errors, connection losses, or disk failures). This makes debugging nearly impossible as failures happen silently.
- Improvement Suggestions: Catch specific exceptions (e.g., `sqlite3.Error`) and implement proper logging or error recovery instead of ignoring the failure.
- Priority Level: Medium

- Code Smell Type: Unpredictable Logic / Non-Deterministic Behavior
- Problem Location: `write_log(message)`: `if random.choice([True, False]): CONN.commit()`
- Detailed Explanation: Committing data to the database based on a random coin flip is highly irregular. This leads to "lost updates" where logs are written to the cursor but never persisted to the database, creating non-deterministic behavior that is extremely hard to reproduce in tests.
- Improvement Suggestions: Remove the random condition. Commit transactions based on a clear business boundary (e.g., at the end of a logical unit of work).
- Priority Level: Medium

- Code Smell Type: Unclear Naming
- Problem Location: `do_business_logic_but_sql_heavy()`
- Detailed Explanation: The function name describes the implementation detail ("sql_heavy") rather than the business intent. Names should reflect *what* the function does, not *how* it does it.
- Improvement Suggestions: Rename the function to reflect its purpose, such as `process_user_activity_logs()` or `simulate_system_events()`.
- Priority Level: Low