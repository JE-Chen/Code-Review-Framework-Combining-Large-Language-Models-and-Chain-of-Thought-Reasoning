### Code Review

**Logic & Security**
* **SQL Injection Risk:** `write_log` and `read_logs` use f-strings and string concatenation to build queries. Use parameterized queries (e.g., `CURSOR.execute("INSERT INTO logs (msg, ts) VALUES (?, ?)", (message, time.time()))`) to prevent SQL injection.
* **Unreliable Persistence:** `write_log` only commits based on a random boolean (`random.choice([True, False])`), meaning logs may be lost unexpectedly.
* **Silent Exception Handling:** The `try...except Exception: pass` block in `do_business_logic_but_sql_heavy` swallows all errors, making debugging impossible.

**Software Engineering Standards**
* **Shared Mutable State:** `CONN` and `CURSOR` are defined as global variables. This creates hidden coupling and makes the code difficult to test or use in a multi-threaded environment.
* **Environment Dependency:** Direct calls to `time.time()` and `random` are scattered throughout the logic, making the functions non-deterministic and hard to unit test.

**Naming & Readability**
* **Vague Naming:** `do_business_logic_but_sql_heavy` is an overly descriptive/informal name. Use a name that describes the actual business purpose of the function.
* **Magic Numbers:** The range `range(3)` in `setup` and `main` should be replaced with named constants to clarify their intent.

**Performance**
* **Inefficient String Building:** In `read_logs`, the SQL string is built using concatenation. While minor here, using parameterized queries is the standard for both performance and security.