## PR Summary

- **Key changes**: Implemented a basic logging system using an in-memory SQLite database, including functions to initialize the schema, write logs, and retrieve formatted log entries.
- **Purpose of changes**: Provide a mechanism for recording and reading application events with timestamps.
- **Risks and considerations**: The current implementation is vulnerable to SQL injection and uses global database connections, which may limit scalability and testability.
- **Items to confirm**: Review the SQL execution patterns and the handling of database transactions.

---

## Code Review

### 1. Logic & Correctness
- **SQL Injection Vulnerability**: In `setup`, `write_log`, and `read_logs`, variables are inserted into SQL strings using f-strings or concatenation. This is a critical security risk. 
    - *Recommendation*: Use parameterized queries (e.g., `CURSOR.execute("INSERT INTO logs (msg, ts) VALUES (?, ?)", (message, time.time()))`).
- **Inconsistent Transaction Management**: In `write_log`, `CONN.commit()` is called randomly (`random.choice([True, False])`). This leads to non-deterministic data persistence and potential data loss.

### 2. Performance & Security
- **Input Validation**: The `message` passed to `write_log` is not validated or sanitized, further exacerbating the SQL injection risk mentioned above.

### 3. Software Engineering Standards
- **Shared Mutable State**: The use of global `CONN` and `CURSOR` objects introduces hidden coupling and makes the code difficult to test in isolation or use in a multi-threaded environment.
    - *Recommendation*: Encapsulate the database logic within a class or pass the connection object as an argument to the functions.
- **Broad Exception Handling**: In `do_business_logic_but_sql_heavy`, there is a `try...except Exception: pass` block. This swallows all errors, making it impossible to debug database failures.
    - *Recommendation*: Catch specific exceptions (e.g., `sqlite3.Error`) and log the error instead of silently ignoring it.

### 4. RAG Rules Compliance
- **Implicit Truthiness**: In `read_logs`, the check `if limit:` relies on implicit truthiness. While common for integers, explicit comparison (e.g., `if limit is not None:`) is preferred for clarity.
- **Single Responsibility**: `do_business_logic_but_sql_heavy` mixes business logic (generating random events) with transaction management (`CONN.commit()`). These responsibilities should be separated.
- **Magic Numbers**: The range `range(3)` in `setup` and `main` are magic numbers. Consider defining these as named constants if they represent specific configuration limits.

### 5. Readability & Consistency
- **Naming**: The function name `do_business_logic_but_sql_heavy` is overly descriptive of the implementation rather than the intent.
    - *Recommendation*: Rename to something reflecting the business purpose, such as `process_user_events`.