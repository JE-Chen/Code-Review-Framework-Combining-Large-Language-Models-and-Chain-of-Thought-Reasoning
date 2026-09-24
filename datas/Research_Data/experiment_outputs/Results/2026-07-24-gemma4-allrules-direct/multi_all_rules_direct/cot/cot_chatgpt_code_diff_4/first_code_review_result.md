### Code Review

**Security & Logic**
*   **SQL Injection Vulnerability:** `write_log` and `setup` use f-strings to insert values into SQL queries. This is a critical security risk. Use parameterized queries (e.g., `CURSOR.execute("INSERT INTO logs (msg, ts) VALUES (?, ?)", (message, time.time()))`).
*   **Unreliable Persistence:** `write_log` only commits the transaction randomly (`random.choice([True, False])`). This leads to unpredictable data loss and inconsistent state.
*   **Broad Exception Handling:** `do_business_logic_but_sql_heavy` uses `except Exception: pass`, which silences all errors and makes debugging impossible.

**Software Engineering Standards**
*   **Shared Mutable State:** `CONN` and `CURSOR` are defined as global variables. This creates hidden coupling and makes the code difficult to test or use in a multi-threaded environment. Pass the connection/cursor as arguments instead.
*   **Single Responsibility Principle:** `do_business_logic_but_sql_heavy` handles business logic, database commits, and data retrieval. These responsibilities should be split.

**Naming & Readability**
*   **Vague Naming:** `do_business_logic_but_sql_heavy` is an unprofessional and non-descriptive function name. Rename it to reflect the actual business purpose (e.g., `process_user_events`).
*   **Magic Numbers:** The range `range(3)` in `setup` and `main` should be replaced with named constants to explain their significance.

**Performance**
*   **Inefficient String Concatenation:** In `read_logs`, the SQL query is built using string addition. While minor here, using parameterized queries is the standard for both security and performance.