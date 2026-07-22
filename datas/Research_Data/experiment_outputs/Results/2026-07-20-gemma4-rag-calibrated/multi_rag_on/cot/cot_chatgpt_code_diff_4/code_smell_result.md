- Code Smell Type: Security Risk (SQL Injection)
- Problem Location: 
  - `setup()`: `f"INSERT INTO logs (msg, ts) VALUES ('init-{i}', {time.time()})"`
  - `write_log(message)`: `sql = f"INSERT INTO logs (msg, ts) VALUES ('{message}', {time.time()})"`
  - `read_logs(limit)`: `base += " LIMIT " + str(limit)`
- Detailed Explanation: The code uses f-strings and string concatenation to build SQL queries. This is a critical security vulnerability known as SQL Injection. If `message` or `limit` were to come from user input, an attacker could execute arbitrary SQL commands, potentially leaking or deleting data.
- Improvement Suggestions: Use parameterized queries (prepared statements). Replace f-strings with `?` placeholders and pass values as a tuple to the `execute` method.
  - Example: `CURSOR.execute("INSERT INTO logs (msg, ts) VALUES (?, ?)", (message, time.time()))`
- Priority Level: High

- Code Smell Type: Shared Mutable State / Tight Coupling
- Problem Location: `CONN = sqlite3.connect(":memory:")` and `CURSOR = CONN.cursor()`
- Detailed Explanation: The database connection and cursor are defined as global variables. This creates hidden coupling across all functions, making the code difficult to test in isolation and preventing the application from scaling to multiple connections or different database configurations without modifying every function.
- Improvement Suggestions: Encapsulate the database logic into a class (e.g., `LogDatabase`) or pass the connection/cursor as arguments to the functions.
- Priority Level: Medium

- Code Smell Type: Environment-Dependent Logic (Non-Deterministic)
- Problem Location: 
  - `write_log(message)`: `if random.choice([True, False]): CONN.commit()`
  - `do_business_logic_but_sql_heavy()`: `random.randint(1, 5)` and `random.choice([None, 2, 5])`
  - `setup()` and `write_log()`: `time.time()`
- Detailed Explanation: The code relies directly on `random` and `time.time()` inside business logic. This makes unit testing nearly impossible because the behavior is non-deterministic and depends on the system clock.
- Improvement Suggestions: Abstract time and randomness. Pass a `clock` or `random_generator` object to the functions, or use a dependency injection pattern so that mocks can be used during testing.
- Priority Level: Medium

- Code Smell Type: Poor Exception Handling (Silent Failure)
- Problem Location: `do_business_logic_but_sql_heavy()`: `except Exception: pass`
- Detailed Explanation: The code catches all exceptions and suppresses them without logging or handling. This "swallowing" of exceptions makes debugging extremely difficult, as database failures (like locking or corruption) will occur silently.
- Improvement Suggestions: Catch specific exceptions (e.g., `sqlite3.Error`) and implement proper logging or error propagation.
- Priority Level: Medium