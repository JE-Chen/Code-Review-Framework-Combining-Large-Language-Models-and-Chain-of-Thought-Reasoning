### Code Review

**Logic & Security**
*   **SQL Injection Vulnerability:** In `setup`, `write_log`, and `read_logs`, variables are inserted into SQL queries using f-strings and string concatenation. Use parameterized queries (e.g., `CURSOR.execute("INSERT INTO logs (msg, ts) VALUES (?, ?)", (message, time.time()))`) to prevent SQL injection.
*   **Unreliable Persistence:** In `write_log`, `CONN.commit()` is called based on a `random.choice([True, False])`. This leads to non-deterministic data persistence and potential data loss.
*   **Silent Exception Handling:** The `try...except Exception: pass` block in `do_business_logic_but_sql_heavy` swallows all errors, making debugging impossible and hiding potential database failures.

**Naming Conventions**
*   **Vague Function Naming:** `do_business_logic_but_sql_heavy` is overly descriptive of the implementation rather than the intent. Rename it to reflect the business purpose (e.g., `process_user_activity`).

**Software Engineering Standards**
*   **Global State:** The use of global `CONN` and `CURSOR` objects makes the code difficult to test and not thread-safe. Consider passing the connection as a dependency or using a context manager.
*   **Resource Management:** While `main()` closes the connection, using a `with` statement for the connection would ensure resources are released even if an exception occurs.

**Readability & Consistency**
*   **Formatting:** The code generally follows PEP 8 standards regarding indentation and spacing.