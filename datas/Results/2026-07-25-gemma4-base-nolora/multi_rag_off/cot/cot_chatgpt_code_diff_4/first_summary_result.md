Here is the code review for `db_app.py` based on the provided global rules.

### 1. Logic & Correctness
*   **Critical: SQL Injection Vulnerability**: In `write_log`, the `message` variable is interpolated directly into the SQL string:
    `sql = f"INSERT INTO logs (msg, ts) VALUES ('{message}', {time.time()})"`
    If `message` contains a single quote (e.g., `"User's login"`), the query will crash. If the input is user-controlled, this allows for arbitrary SQL execution.
    **Recommendation**: Use parameterized queries: `CURSOR.execute("INSERT INTO logs (msg, ts) VALUES (?, ?)", (message, time.time()))`.
*   **Potential Bug: Unstable `read_logs` limit**: In `read_logs`, the `limit` is concatenated as a string. While currently passed as an integer from `do_business_logic_but_sql_heavy`, this is a bad practice that could lead to crashes or injections if the function is ever exposed to external input.
    **Recommendation**: Use parameterized queries for the limit or cast strictly to `int`.

### 2. Performance & Security
*   **Resource Management**: The `CONN` and `CURSOR` are defined as global variables. While acceptable for a small script, in a larger application, this prevents thread safety and makes testing difficult.
*   **Inefficient Commits**: In `write_log`, `CONN.commit()` is called randomly (`random.choice([True, False])`). This leads to unpredictable transaction boundaries and potential data loss if the program terminates before a commit occurs.

### 3. Software Engineering Standards
*   **Exception Handling**: In `do_business_logic_but_sql_heavy`, there is a "bare except" block:
    ```python
    try:
        CONN.commit()
    except Exception:
        pass
    ```
    Silencing all exceptions is dangerous as it hides database corruption, disk full errors, or connection losses, making debugging nearly impossible.
    **Recommendation**: Catch specific SQLite exceptions or log the error.

### 4. Readability & Consistency
*   **Naming**: The function name `do_business_logic_but_sql_heavy` is overly verbose and descriptive of the implementation rather than the intent.
    **Recommendation**: Rename to something reflecting the business purpose (e.g., `process_user_activity`).
*   **Formatting**: The code generally follows PEP 8 standards regarding indentation and spacing.

### 5. Documentation & Testing
*   **Missing Documentation**: There are no docstrings for the functions. It is unclear what `setup()` is intended to initialize beyond the basic table.
*   **Testing**: No unit tests are provided for the logic, particularly for the `read_logs` filtering.

---

### Summary of Findings
| Category | Severity | Issue |
| :--- | :--- | :--- |
| **Security** | 🔴 High | SQL Injection in `write_log` |
| **Correctness** | 🟡 Medium | Unstable transaction commits |
| **Engineering** | 🟡 Medium | Silent exception swallowing (`pass`) |
| **Readability** | 🔵 Low | Non-standard function naming |