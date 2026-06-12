This code review is conducted based on the provided global rules.

### ⚠️ Critical Warning: Security Vulnerability
The most significant issue in this code is the presence of **SQL Injection vulnerabilities**.

---

### 1. Readability & Consistency
- **Formatting:** The code follows PEP 8 generally and is well-indented.
- **Consistency:** The use of uppercase for `CONN` and `CURSOR` suggests they are constants, but they are mutable state objects. This is slightly misleading.

### 2. Naming Conventions
- **Function Naming:** `do_business_logic_but_sql_heavy` is too descriptive/informal. It should be named based on its purpose (e.g., `process_user_activity_logs`), not its implementation detail (sql_heavy).
- **Variable Naming:** `base` in `read_logs` is acceptable, but `query` would be more semantic.

### 3. Software Engineering Standards
- **Modularity:** The code uses global objects (`CONN`, `CURSOR`). This makes the code difficult to test in parallel and prevents the application from handling multiple database connections.
- **Dependency Injection:** It is recommended to pass the connection or session as an argument to functions rather than relying on global state.
- **Resource Management:** The connection is closed in `main()`, but if an exception occurs during the loop, the connection remains open. Use a `try...finally` block or a context manager.

### 4. Logic & Correctness
- **Transaction Management:** The `write_log` function uses `random.choice([True, False])` to decide whether to commit. This introduces non-deterministic behavior where data may or may not be persisted, which is generally unacceptable in a production system.
- **Exception Handling:** The `try...except Exception: pass` in `do_business_logic_but_sql_heavy` is a **silent failure**. This masks database errors and makes debugging impossible.

### 5. Performance & Security
- **🚨 SQL Injection (High Risk):** 
    - In `setup()`, `write_log()`, and `read_logs()`, variables are inserted into SQL strings using f-strings or concatenation.
    - **Example:** `f"INSERT INTO logs ... VALUES ('{message}', ...)"`
    - **Fix:** Use parameterized queries: `CURSOR.execute("INSERT INTO logs (msg, ts) VALUES (?, ?)", (message, time.time()))`.
- **Performance:** The code performs multiple individual `INSERT` statements in a loop. For higher volumes, batch inserts (`executemany`) would be more efficient.

### 6. Documentation & Testing
- **Documentation:** There are no docstrings explaining the purpose of the functions.
- **Testing:** No unit tests are provided. The `main()` function acts as a smoke test but does not validate correctness or edge cases (e.g., empty tables, special characters in messages).

---

### Summary of Recommendations

| Category | Issue | Severity | Recommendation |
| :--- | :--- | :--- | :--- |
| **Security** | SQL Injection | 🚨 Critical | Switch to parameterized queries immediately. |
| **Logic** | Non-deterministic Commits | 🔴 High | Remove `random.choice` from `CONN.commit()`. |
| **Engineering** | Global State | 🟡 Medium | Pass DB connection as a parameter to functions. |
| **Engineering** | Silent Exceptions | 🟡 Medium | Remove `pass` in `except` blocks; log the error. |
| **Naming** | Informal function names | 🟢 Low | Rename `do_business_logic_but_sql_heavy` to something semantic. |

**Verdict:** **Request Changes.** The security vulnerabilities and non-deterministic transaction logic must be addressed before this code can be merged.