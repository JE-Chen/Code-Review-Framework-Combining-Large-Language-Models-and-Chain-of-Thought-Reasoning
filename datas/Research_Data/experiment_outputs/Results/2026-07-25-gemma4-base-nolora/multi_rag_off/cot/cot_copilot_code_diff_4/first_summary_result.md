This code review is conducted based on the provided global rules.

### 🚩 Critical Issues

**1. Security: SQL Injection Vulnerability**
*   **Location:** Lines 20 and 24.
*   **Issue:** The code uses string concatenation to build SQL queries (`"VALUES('" + name + "', " + str(age) + ")"`). This is a severe security risk that allows for SQL Injection attacks.
*   **Recommendation:** Always use parameterized queries. 
    *   *Correct:* `cursorThing.execute("INSERT INTO users(name, age) VALUES(?, ?)", (name, age))`

**2. Logic & Correctness: Resource Management**
*   **Location:** Lines 11–38.
*   **Issue:** The database connection and cursor are managed manually. If an exception occurs during the `INSERT` or `SELECT` phases, `conn.close()` may never be called, leading to potential memory leaks or locked database files.
*   **Recommendation:** Use a `with` statement (context manager) for both the connection and the cursor to ensure resources are closed automatically.

---

### 🛠️ Engineering & Readability Improvements

**3. Naming Conventions**
*   **Location:** Throughout the file.
*   **Issue:** Several names violate standard Python (PEP 8) conventions and lack semantic clarity:
    *   `cursorThing`: Non-descriptive. Use `cursor`.
    *   `functionThatDoesTooManyThingsAndIsHardToRead`: Extremely verbose and self-deprecating; does not describe the *purpose* of the function. Use something like `setup_and_query_users`.
    *   `anotherName`/`anotherAge`: Use a list or a loop to handle multiple entries rather than numbered/prefixed variables.

**4. Software Engineering Standards (Modularity)**
*   **Location:** `functionThatDoesTooManyThingsAndIsHardToRead`
*   **Issue:** The function violates the Single Responsibility Principle. It handles connection management, schema creation, data insertion, and data reporting all in one block.
*   **Recommendation:** Split this into smaller functions: `init_db()`, `add_user(name, age)`, and `print_users()`.

**5. Error Handling**
*   **Location:** Lines 16 and 34.
*   **Issue:** 
    *   The code uses "bare" `except` blocks or catches the generic `Exception` class and prints that it will "ignore" the error. This hides bugs and makes debugging nearly impossible.
    *   The print statements are inconsistent (mixing English and Chinese).
*   **Recommendation:** Catch specific exceptions (e.g., `sqlite3.Error`) and implement proper logging or error propagation.

**6. Readability & Consistency**
*   **Location:** Lines 28–33.
*   **Issue:** Deeply nested `if/else` blocks make the logic harder to follow.
*   **Recommendation:** Use a flatter structure or a mapping dictionary to handle the print logic.

---

### 📊 Summary Scorecard

| Category | Rating | Notes |
| :--- | :--- | :--- |
| **Readability** | 🔴 Poor | Poor naming and deep nesting. |
| **Naming** | 🔴 Poor | Non-standard and non-descriptive. |
| **Engineering** | 🔴 Poor | Lacks modularity; violates SRP. |
| **Correctness** | 🟡 Fair | Logic works for a happy path, but resource handling is risky. |
| **Security** | 🔴 Critical | High risk of SQL Injection. |
| **Documentation** | 🔴 Poor | No docstrings or meaningful comments. |

**Verdict:** **Request Changes.** The security vulnerability (SQL Injection) and lack of modularity must be addressed before this code can be merged.