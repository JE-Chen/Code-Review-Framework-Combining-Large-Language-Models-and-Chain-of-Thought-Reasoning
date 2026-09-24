## PR Summary

*   **Key changes**: Implemented a basic SQLite-based logging system with functions to initialize the database, write logs, and retrieve them.
*   **Purpose of changes**: Provides a mechanism for recording and reading system events in-memory.
*   **Risks and considerations**: The current implementation is vulnerable to SQL injection and uses global database connections, which may limit scalability and testability.
*   **Items to confirm**: Review the security of SQL query construction and the management of the database connection lifecycle.

---

## Code Review

### 1. Logic & Correctness
*   **SQL Injection Vulnerability**: In `write_log` and `setup`, variables are inserted into SQL strings using f-strings (e.g., `f"INSERT INTO logs ... VALUES ('{message}', ...)"`). This is a critical security risk.
    *   **Recommendation**: Use parameterized queries: `CURSOR.execute("INSERT INTO logs (msg, ts) VALUES (?, ?)", (message, time.time()))`.
*   **Inconsistent Commits**: In `write_log`, `CONN.commit()` is called based on a `random.choice([True, False])`. This leads to non-deterministic data persistence and potential data loss.
*   **Silent Exception Handling**: In `do_business_logic_but_sql_heavy`, the `try...except Exception: pass` block swallows all errors during commit, making it impossible to debug database failures.

### 2. Performance & Security
*   **SQL Injection**: (As noted above) The use of string formatting for queries allows for arbitrary SQL execution if `message` is user-controlled.

### 3. Software Engineering Standards
*   **Shared Mutable State**: The use of global `CONN` and `CURSOR` objects creates hidden coupling and makes the code difficult to test in parallel or reset between test cases.
    *   **Recommendation**: Pass the connection/cursor as arguments to functions or encapsulate them in a class.
*   **Hard-coded Constants**: The log messages in `do_business_logic_but_sql_heavy` are hard-coded inside the loop.

### 4. RAG Rules Compliance
*   **Environment-Dependent Logic**: The code calls `time.time()` and `random.randint/choice` directly inside business logic. This makes the output non-deterministic and difficult to unit test.
    *   **Recommendation**: Abstract time and randomness into a provider or pass them as arguments.
*   **Implicit Truthiness**: In `read_logs`, `if limit:` is used. While acceptable for integers, explicit comparison (e.g., `if limit is not None:`) is preferred to avoid ambiguity if `0` is a valid limit.

### 5. Readability & Consistency
*   **Naming**: `do_business_logic_but_sql_heavy` is an overly verbose and non-standard function name. It should describe the *intent* of the business logic rather than the *implementation detail* (SQL heaviness).