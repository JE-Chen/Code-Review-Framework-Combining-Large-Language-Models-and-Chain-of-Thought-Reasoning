### Pull Request Summary

*   **Key changes**: Introduced a new SQLite-based logging application (`db_app.py`) with functionality to initialize a database, write logs, and retrieve them.
*   **Purpose of changes**: Implementation of a basic database-backed logging system for business logic tracking.
*   **Risks and considerations**: The current implementation is vulnerable to SQL injection and lacks robust transaction management.
*   **Items to confirm**: Review the security of SQL query construction and the consistency of database commits.

---

### Code Review

#### 1. Logic & Correctness
*   **SQL Injection Vulnerability**: In `write_log` and `read_logs`, variables are inserted into SQL strings using f-strings and string concatenation. This is a critical security risk.
    *   *Recommendation*: Use parameterized queries (e.g., `CURSOR.execute("INSERT INTO logs (msg, ts) VALUES (?, ?)", (message, time.time()))`).
*   **Inconsistent Transaction Management**: In `write_log`, `CONN.commit()` is called randomly (`random.choice([True, False])`). This leads to non-deterministic data persistence and potential data loss.
*   **Silent Exception Handling**: In `do_business_logic_but_sql_heavy`, the `try...except Exception: pass` block swallows all errors during commit, making it impossible to debug database failures.

#### 2. Software Engineering Standards
*   **Global State**: The use of global `CONN` and `CURSOR` objects makes the code difficult to test in parallel and limits the application to a single database connection.
    *   *Recommendation*: Pass the connection/cursor as arguments to functions or encapsulate them within a class.
*   **Modularization**: The `setup` function mixes schema creation with seed data insertion. These should be separated for better maintainability.

#### 3. Performance & Security
*   **Resource Management**: While `main()` closes the connection, the application does not use a context manager (`with` statement). If an exception occurs before the end of `main()`, the connection may remain open.
*   **Input Validation**: There is no validation on the `limit` parameter in `read_logs` other than casting it to a string, which further exposes the app to SQL injection if `limit` were to come from user input.

#### 4. Readability & Consistency
*   **Naming**: The function name `do_business_logic_but_sql_heavy` is overly verbose and non-standard.
    *   *Recommendation*: Rename to something descriptive like `process_business_logs`.

#### 5. Documentation & Testing
*   **Missing Tests**: No unit tests are provided for the database operations.
*   **Missing Docstrings**: None of the functions have docstrings explaining their purpose, arguments, or return values.