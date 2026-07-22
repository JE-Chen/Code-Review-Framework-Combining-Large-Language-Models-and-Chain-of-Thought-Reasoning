### Code Review

**Logic & Security**
* **SQL Injection Vulnerability:** The `write_log` and `read_logs` functions use f-strings and string concatenation to build queries. Use parameterized queries (e.g., `CURSOR.execute("INSERT INTO logs (msg, ts) VALUES (?, ?)", (message, time.time()))`) to prevent SQL injection.
* **Unreliable Persistence:** In `write_log`, `CONN.commit()` is called randomly (`random.choice([True, False])`). This leads to non-deterministic data persistence and potential data loss.
* **Silent Exception Handling:** The `try...except Exception: pass` block in `do_business_logic_but_sql_heavy` swallows all errors, making debugging impossible.

**Software Engineering Standards**
* **Global State:** The use of global `CONN` and `CURSOR` objects limits the code's testability and prevents the application from being thread-safe or supporting multiple database connections.
* **Resource Management:** While `main()` closes the connection, using a context manager (`with sqlite3.connect(...) as conn:`) is the standard practice to ensure resources are released even if an exception occurs.

**Naming Conventions**
* **Function Naming:** `do_business_logic_but_sql_heavy` is overly verbose and descriptive of the implementation rather than the intent. Suggest a name like `process_logs` or `execute_business_workflow`.

**Readability & Consistency**
* **Formatting:** The code is generally well-formatted and follows PEP 8 indentation and spacing.