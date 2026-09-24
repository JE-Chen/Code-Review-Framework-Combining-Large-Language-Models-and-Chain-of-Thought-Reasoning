## PR Summary

*   **Key changes**: Implemented a basic logging application using an in-memory SQLite database, including functions to initialize the schema, write logs, and retrieve them.
*   **Purpose of changes**: Initial implementation of a database-backed logging utility.
*   **Risks and considerations**: The current implementation is vulnerable to SQL injection and uses shared global state, which will hinder scalability and security.
*   **Items to confirm**: Review the SQL execution patterns and the use of global connection objects.

---

## Code Review

### 1. Logic & Correctness
*   **Critical: SQL Injection Vulnerability**: In `write_log` and `setup`, variables are inserted into SQL strings using f-strings (e.g., `f"INSERT INTO logs ... VALUES ('{message}', ...)"`). This is a severe security risk. 
    *   **Fix**: Use parameterized queries: `CURSOR.execute("INSERT INTO logs (msg, ts) VALUES (?, ?)", (message, time.time()))`.
*   **Potential Bug: Unstable `read_logs`**: In `read_logs`, the `limit` is appended via string concatenation. While `limit` is currently passed as an integer from `do_business_logic_but_sql_heavy`, this is still a poor practice that could lead to crashes or injection if the input source changes.

### 2. Performance & Security
*   **Resource Management**: The `CONN` and `CURSOR` are defined as global constants. While acceptable for a tiny script, this creates shared mutable state that makes the code non-thread-safe and difficult to test.
*   **Inefficient Commits**: In `write_log`, `CONN.commit()` is called randomly (`random.choice([True, False])`). This leads to unpredictable persistence behavior and unnecessary I/O overhead.

### 3. Software Engineering Standards
*   **Shared Mutable State**: The use of global `CONN` and `CURSOR` violates the RAG rule regarding shared mutable state at the module level. This couples all functions to a single database instance.
    *   **Recommendation**: Pass the connection or cursor as an argument to the functions.
*   **Exception Handling**: In `do_business_logic_but_sql_heavy`, there is a "bare" except block:
    ```python
    try:
        CONN.commit()
    except Exception:
        pass
    ```
    Swallowing all exceptions without logging them makes debugging nearly impossible.

### 4. RAG Rules Compliance
*   **Time-Dependent Logic**: The code calls `time.time()` directly inside `setup` and `write_log`. This makes the logic environment-dependent and difficult to unit test deterministically.
    *   **Recommendation**: Pass the timestamp as an argument or use a provider abstraction.
*   **Magic Numbers**: The range `range(3)` in `setup` and `main`, and the random range `random.randint(1, 5)` are magic numbers. These should be defined as named constants at the top of the file.
*   **Implicit Truthiness**: In `read_logs`, `if limit:` is used. While it works for integers, it is safer to be explicit (e.g., `if limit is not None:`) to avoid issues if `0` is ever passed as a valid limit.

### 5. Readability & Consistency
*   **Naming**: The function name `do_business_logic_but_sql_heavy` is overly verbose and non-standard. A name like `process_logs` or `execute_log_cycle` would be more professional.