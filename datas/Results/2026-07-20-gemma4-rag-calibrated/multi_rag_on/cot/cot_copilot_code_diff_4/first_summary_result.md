## PR Summary

*   **Key changes**: Implemented a basic SQLite database application to create a `users` table and insert/query records.
*   **Purpose of changes**: Initial setup for user data persistence.
*   **Items to confirm**: Review the security of SQL execution and the overall structure of the database connection management.

---

## Code Review

### 1. Readability & Consistency
*   **Naming Conventions**: 
    *   `functionThatDoesTooManyThingsAndIsHardToRead` is not a descriptive or professional name. It should be renamed to reflect its purpose (e.g., `initialize_and_test_user_db`).
    *   `cursorThing` is vague. Use `cursor`.
    *   `anotherName` and `anotherAge` use camelCase, which deviates from the PEP 8 standard (snake_case) used for `name` and `age`.
*   **Formatting**: The nested `if/else` block for printing users is overly deep and reduces readability.

### 2. Software Engineering Standards
*   **Modularity**: The function violates the Single Responsibility Principle. It handles connection management, schema creation, data insertion, and data retrieval all in one block. These should be split into separate functions (e.g., `create_table()`, `add_user()`, `get_users()`).
*   **Resource Management**: The connection and cursor are managed using global variables and manual `close()` calls. This is error-prone. Use a context manager (`with sqlite3.connect(...) as conn:`) to ensure resources are closed even if an exception occurs.

### 3. Logic & Correctness
*   **Exception Handling**: 
    *   The `try...except` blocks are too broad. Catching `Exception` or using a bare `except:` hides bugs and makes debugging difficult.
    *   The error messages ("I will ignore", "但我不在乎") are unprofessional and do not provide actionable information for troubleshooting.

### 4. Performance & Security
*   **Critical Security Risk (SQL Injection)**: The code uses string concatenation to build SQL queries:
    `"INSERT INTO users(name, age) VALUES('" + name + "', " + str(age) + ")"`
    This is a severe security vulnerability. **Always use parameterized queries** to prevent SQL injection:
    `cursor.execute("INSERT INTO users(name, age) VALUES(?, ?)", (name, age))`

### 5. Documentation & Testing
*   **Documentation**: There are no docstrings or comments explaining the purpose of the logic.
*   **Testing**: No unit tests are provided to verify the database operations.

### Summary of Required Changes
1.  **Fix SQL Injection**: Switch to parameterized queries immediately.
2.  **Refactor**: Break the monolithic function into smaller, reusable functions.
3.  **Clean up Naming**: Rename functions and variables to follow PEP 8 and be descriptive.
4.  **Improve Error Handling**: Use specific exceptions and professional logging/reporting.
5.  **Resource Management**: Implement `with` statements for database connections.