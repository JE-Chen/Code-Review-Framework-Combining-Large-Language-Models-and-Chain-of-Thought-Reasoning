### Code Review: `db_app.py`

**Logic & Security**
*   **SQL Injection Vulnerability:** The `write_log` and `read_logs` functions use f-strings and string concatenation to build queries. This is a critical security risk. Use parameterized queries instead (e.g., `CURSOR.execute("INSERT INTO logs (msg, ts) VALUES (?, ?)", (message, time.time()))`).
*   **Unreliable Persistence:** In `write_log`, `CONN.commit()` is called based on a `random.choice([True, False])`. This means logs may be lost unexpectedly, which is generally unacceptable for a logging system.
*   **Silent Exception Handling:** The `try...except Exception: pass` block in `do_business_logic_but_sql_heavy` swallows all errors, making debugging impossible if a database commit fails.

**Software Engineering Standards**
*   **Global State:** The use of global `CONN` and `CURSOR` objects makes the code difficult to test and prevents the application from being thread-safe or supporting multiple database connections.
*   **Resource Management:** While `main()` closes the connection, it is safer to use a context manager (`with sqlite3.connect(...) as conn:`) to ensure resources are released even if an exception occurs.

**Naming & Readability**
*   **Function Naming:** `do_business_logic_but_sql_heavy` is overly verbose and descriptive of the implementation rather than the intent. Suggest a name like `process_user_activity` or `run_business_cycle`.
*   **Variable Naming:** In `read_logs`, the variable `base` is used for the SQL query; `query` or `sql` would be more standard.

**Performance**
*   **Inefficient String Building:** In `read_logs`, the limit is appended via string concatenation. While minor here, using parameterized queries (as noted in Security) is the performant and standard way to handle dynamic values in SQL.