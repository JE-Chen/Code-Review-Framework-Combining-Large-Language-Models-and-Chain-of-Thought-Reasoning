- Code Smell Type: SQL Injection Vulnerability
- Problem Location: 
  - `setup()`: `f"INSERT INTO logs (msg, ts) VALUES ('init-{i}', {time.time()})"`
  - `write_log(message)`: `sql = f"INSERT INTO logs (msg, ts) VALUES ('{message}', {time.time()})"`
  - `read_logs(limit)`: `base += " LIMIT " + str(limit)`
- Detailed Explanation: The code uses f-strings and string concatenation to build SQL queries. This is a critical security flaw. If `message` or `limit` were to come from user input, an attacker could inject malicious SQL commands to manipulate or delete data. Even in internal apps, this leads to crashes if a message contains a single quote (e.g., "User's login").
- Improvement Suggestions: Use parameterized queries (prepared statements). Replace f-strings with `?` placeholders and pass values as a tuple to the `execute` method.
  - Example: `CURSOR.execute("INSERT INTO logs (msg, ts) VALUES (?, ?)", (message, time.time()))`
- Priority Level: High

- Code Smell Type: Unreliable Data Persistence (Non-Deterministic Commits)
- Problem Location: `write_log(message)`: `if random.choice([True, False]): CONN.commit()`
- Detailed Explanation: Committing transactions based on a random boolean is logically incorrect. This means logs may or may not be persisted to the database unpredictably. In a real-world scenario, this leads to data loss and makes debugging impossible as the state of the database is non-deterministic.
- Improvement Suggestions: Remove the random condition. Commit the transaction consistently after a logical unit of work is completed, or use a context manager for transactions.
- Priority Level: High

- Code Smell Type: Silent Exception Swallowing
- Problem Location: `do_business_logic_but_sql_heavy()`: `except Exception: pass`
- Detailed Explanation: Catching the base `Exception` class and doing nothing (`pass`) hides all potential errors (connection issues, disk full, schema mismatches). This makes the system fail silently, preventing developers from identifying and fixing the root cause of crashes.
- Improvement Suggestions: Catch specific exceptions (e.g., `sqlite3.Error`) and log the error message using a logging framework or re-raise the exception after cleanup.
- Priority Level: Medium

- Code Smell Type: Global State / Tight Coupling
- Problem Location: `CONN = sqlite3.connect(":memory:")` and `CURSOR = CONN.cursor()`
- Detailed Explanation: The database connection and cursor are defined as global variables. This makes the code difficult to test (unit tests will share state), prevents the app from scaling to multiple connections, and creates tight coupling between the functions and a specific global instance.
- Improvement Suggestions: Encapsulate the database logic into a class (e.g., `LogDatabase`) or pass the connection/cursor as arguments to the functions.
- Priority Level: Medium