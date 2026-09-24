- Code Smell Type: Security Risk (SQL Injection)
- Problem Location: 
  - `setup()`: `f"INSERT INTO logs (msg, ts) VALUES ('init-{i}', {time.time()})"`
  - `write_log(message)`: `sql = f"INSERT INTO logs (msg, ts) VALUES ('{message}', {time.time()})"`
  - `read_logs(limit)`: `base += " LIMIT " + str(limit)`
- Detailed Explanation: The code uses Python f-strings and string concatenation to build SQL queries. This is a critical security vulnerability known as SQL Injection. If the `message` or `limit` arguments were to come from user input, an attacker could execute arbitrary SQL commands, potentially deleting data or bypassing security checks.
- Improvement Suggestions: Use parameterized queries (prepared statements). Replace f-strings with placeholders (`?` for sqlite3) and pass the values as a tuple to the `execute` method.
  - Example: `CURSOR.execute("INSERT INTO logs (msg, ts) VALUES (?, ?)", (message, time.time()))`
- Priority Level: High

- Code Smell Type: Shared Mutable State / Tight Coupling
- Problem Location: `CONN = sqlite3.connect(":memory:")` and `CURSOR = CONN.cursor()`
- Detailed Explanation: The database connection and cursor are defined as global variables. This creates hidden coupling across all functions, making the code difficult to test in isolation (unit testing) and preventing the application from being thread-safe or supporting multiple database connections. It violates the principle of avoiding shared mutable state at the module level.
- Improvement Suggestions: Encapsulate the database logic within a class (e.g., `DatabaseManager`) or pass the connection/cursor as arguments to the functions that require them.
- Priority Level: High

- Code Smell Type: Environment-Dependent Logic (Non-Deterministic)
- Problem Location: 
  - `write_log(message)`: `if random.choice([True, False]): CONN.commit()`
  - `do_business_logic_but_sql_heavy()`: `range(random.randint(1, 5))` and `limit=random.choice([None, 2, 5])`
- Detailed Explanation: The business logic relies directly on `random` and `time.time()` calls. This makes the behavior of the application non-deterministic, which makes debugging and writing reliable unit tests nearly impossible because the output changes every time the code is run.
- Improvement Suggestions: Abstract the time and randomness providers. Pass these values as arguments to the functions or use a dependency injection pattern so that mocks can be used during testing.
- Priority Level: Medium

- Code Smell Type: Poor Exception Handling (Silent Failure)
- Problem Location: `do_business_logic_but_sql_heavy()`: `except Exception: pass`
- Detailed Explanation: The code uses a "bare except" block that catches all exceptions and does nothing with them. This is a dangerous practice as it hides bugs (like connection losses or syntax errors) and makes it impossible to diagnose why a commit might be failing.
- Improvement Suggestions: Catch specific exceptions (e.g., `sqlite3.Error`) and implement proper logging or error recovery logic instead of silently ignoring the failure.
- Priority Level: Medium

- Code Smell Type: Magic Numbers
- Problem Location: `setup()`: `range(3)`, `main()`: `range(3)`, `time.sleep(0.2)`
- Detailed Explanation: Hard-coded integers are scattered throughout the code. It is unclear why the loop runs exactly 3 times or why the sleep duration is 0.2 seconds. This reduces maintainability.
- Improvement Suggestions: Define these as named constants at the top of the file (e.g., `INITIAL_LOG_COUNT = 3`, `POLLING_INTERVAL = 0.2`).
- Priority Level: Low