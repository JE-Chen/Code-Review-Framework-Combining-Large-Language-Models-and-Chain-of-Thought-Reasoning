- Code Smell Type: SQL Injection Vulnerability
- Problem Location: 
  - `setup()`: `f"INSERT INTO logs (msg, ts) VALUES ('init-{i}', {time.time()})"`
  - `write_log(message)`: `sql = f"INSERT INTO logs (msg, ts) VALUES ('{message}', {time.time()})"`
  - `read_logs(limit)`: `base += " LIMIT " + str(limit)`
- Detailed Explanation: The code uses Python f-strings and string concatenation to build SQL queries. This allows raw input to be executed as SQL commands. While the current `main()` uses hardcoded strings, any change that allows user-provided input into `write_log` or `read_logs` would lead to a critical security vulnerability (SQL Injection).
- Improvement Suggestions: Use parameterized queries (prepared statements). Replace f-strings with `?` placeholders and pass values as a tuple to the `execute` method.
  - Example: `CURSOR.execute("INSERT INTO logs (msg, ts) VALUES (?, ?)", (message, time.time()))`
- Priority Level: High

- Code Smell Type: Unreliable Data Persistence (Non-Deterministic Commits)
- Problem Location: `write_log(message)`: `if random.choice([True, False]): CONN.commit()`
- Detailed Explanation: The decision to commit data to the database is based on a random coin flip. This leads to non-deterministic behavior where logs may be lost if the application crashes or closes before a random commit occurs. It violates the principle of atomicity and reliability in database transactions.
- Improvement Suggestions: Remove the random condition. Commit transactions based on logical business boundaries (e.g., at the end of a unit of work in `do_business_logic_but_sql_heavy`) or after every critical write if immediate persistence is required.
- Priority Level: High

- Code Smell Type: Silent Exception Swallowing
- Problem Location: `do_business_logic_but_sql_heavy()`: `except Exception: pass`
- Detailed Explanation: The code catches all possible exceptions during `CONN.commit()` and ignores them completely. This hides critical failures (e.g., disk full, database corruption, locking issues), making the system impossible to debug and potentially leaving the application in an inconsistent state.
- Improvement Suggestions: Remove the empty `except` block. Either allow the exception to bubble up to a global error handler or log the specific error using a logging library so that failures are visible.
- Priority Level: Medium

- Code Smell Type: Global State / Tight Coupling
- Problem Location: `CONN = sqlite3.connect(":memory:")` and `CURSOR = CONN.cursor()`
- Detailed Explanation: The database connection and cursor are defined as global variables. This makes the code difficult to test (unit tests will share the same state), prevents the app from handling multiple database connections, and creates tight coupling between the functions and a specific global instance.
- Improvement Suggestions: Use a dependency injection pattern. Pass the connection or a database session object as an argument to the functions that require it, or wrap the database logic in a Class/Repository pattern.
- Priority Level: Medium