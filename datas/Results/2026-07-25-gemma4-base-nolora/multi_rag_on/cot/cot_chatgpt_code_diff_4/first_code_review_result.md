### Code Review

**Logic & Security**
*   **SQL Injection Vulnerability:** The `setup`, `write_log`, and `read_logs` functions use f-strings and string concatenation to build queries. This is a critical security risk. Use parameterized queries (e.g., `CURSOR.execute("INSERT INTO logs (msg, ts) VALUES (?, ?)", (message, time.time()))`).
*   **Unreliable Persistence:** In `write_log`, `CONN.commit()` is called based on a `random.choice`. This means logs may be lost or not persisted unpredictably.
*   **Silent Exception Handling:** The `try...except Exception: pass` block in `do_business_logic_but_sql_heavy` swallows all errors, making debugging impossible.

**Software Engineering Standards**
*   **Shared Mutable State:** `CONN` and `CURSOR` are defined as global variables. This creates hidden coupling and makes the code difficult to test or use in a multi-threaded environment. Pass the connection/cursor as arguments instead.
*   **Hard-coded Constants:** The log messages in `do_business_logic_but_sql_heavy` are hard-coded strings. These should be moved to a named constant or configuration list.

**RAG Rule Violations**
*   **Environment-Dependent Logic:** Direct calls to `time.time()` and `random` are scattered throughout the logic. These should be abstracted or injected to allow for deterministic unit testing.
*   **Implicit Truthiness:** In `read_logs`, `if limit:` relies on implicit truthiness. Use `if limit is not None:` to explicitly handle the case where a limit of `0` might be passed.

**Readability & Naming**
*   **Vague Naming:** The function name `do_business_logic_but_sql_heavy` is overly descriptive/informal and does not describe the *intent* of the business logic.
*   **Formatting:** The code generally follows PEP 8, but the logic flow in `read_logs` (string concatenation for SQL) is brittle.