### Code Review

#### 1. Readability & Consistency
- **Formatting**: The code is generally well-formatted and follows PEP 8 standards.
- **Consistency**: The use of uppercase for global constants (`CONN`, `CURSOR`) is consistent.

#### 2. Naming Conventions
- **Descriptive Names**: Function names like `do_business_logic_but_sql_heavy` are overly verbose and unconventional. A name like `process_business_logs` would be more professional.

#### 3. Software Engineering Standards
- **Modularity**: The database connection and cursor are defined as global variables. This makes the code difficult to test in isolation and prevents the application from scaling to multiple connections or threads.
- **Resource Management**: While `main()` closes the connection, the `setup()` and `write_log()` functions rely on a shared global state, which is a fragile pattern.

#### 4. Logic & Correctness
- **SQL Injection (Critical)**: The code uses f-strings to build SQL queries in `setup`, `write_log`, and `read_logs`.
    - In `write_log(message)`, if `message` contains a single quote (e.g., `"User's login"`), the query will crash or allow for SQL injection.
    - In `read_logs(limit)`, the `limit` is concatenated directly into the string.
    - **Fix**: Use parameterized queries: `CURSOR.execute("INSERT INTO logs (msg, ts) VALUES (?, ?)", (message, time.time()))`.
- **Exception Handling**: The `try...except Exception: pass` block in `do_business_logic_but_sql_heavy` is a "silent failure" pattern. Swallowing all exceptions makes debugging impossible and can hide critical database corruption or connection issues.

#### 5. Performance & Security
- **Security**: As mentioned in "Logic & Correctness," the lack of input sanitization/parameterization is a high-security risk.
- **Performance**: The `write_log` function commits randomly (`random.choice([True, False])`). In a real-world scenario, frequent commits to a disk-based DB would be a bottleneck, and inconsistent commits lead to unpredictable data persistence.

#### 6. Documentation & Testing
- **Documentation**: There are no docstrings explaining the purpose of the functions or the expected types of the arguments.
- **Testing**: No unit tests are provided for the logic.

---

### Summary of Findings

| Category | Severity | Issue |
| :--- | :--- | :--- |
| **Security** | Critical | SQL Injection vulnerability due to f-string query construction. |
| **Logic** | High | Silent exception handling (`pass`) in business logic. |
| **Architecture** | Medium | Reliance on global database state (`CONN`, `CURSOR`). |
| **Readability** | Low | Unprofessional function naming. |