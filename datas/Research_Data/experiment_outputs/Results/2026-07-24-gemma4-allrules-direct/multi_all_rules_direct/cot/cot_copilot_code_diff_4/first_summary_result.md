## PR Summary

*   **Key changes**: Introduced `sql_app.py` to handle basic SQLite database operations (table creation, data insertion, and querying).
*   **Impact scope**: New file `sql_app.py`.
*   **Purpose of changes**: Initial implementation of user data persistence.
*   **Items to confirm**: Review the database connection management and security of SQL execution.

---

## Code Review

### 1. Logic & Correctness
*   **Security Risk (SQL Injection)**: The code uses string concatenation to build SQL queries:
    `"INSERT INTO users(name, age) VALUES('" + name + "', " + str(age) + ")"`
    This is a critical security vulnerability. **Always use parameterized queries** (e.g., `cursor.execute("INSERT INTO users(name, age) VALUES(?, ?)", (name, age))`) to prevent SQL injection.

### 2. Naming Conventions
*   **Non-Descriptive Names**: `functionThatDoesTooManyThingsAndIsHardToRead` and `cursorThing` are not professional or descriptive. Use names that reflect the intent, such as `initialize_user_database` and `cursor`.
*   **Consistency**: The code mixes `camelCase` (`anotherName`, `cursorThing`) with `snake_case` (standard for Python). Please follow PEP 8 naming conventions.

### 3. Software Engineering Standards
*   **Single Responsibility Principle**: The function handles connection management, schema creation, data seeding, and data retrieval. These should be split into smaller, focused functions (e.g., `create_table()`, `add_user()`, `get_users()`).
*   **Shared Mutable State**: The use of `global conn, cursorThing` introduces hidden coupling and makes the code difficult to test or reuse in a multi-threaded environment. Pass the connection object as an argument instead.

### 4. Performance & Security
*   **Resource Management**: While `conn.close()` is called at the end, if an exception occurs before that line, the connection remains open. Use a `with` statement (context manager) for both the connection and the cursor to ensure resources are closed automatically.

### 5. RAG Rule Violations
*   **Broad Exception Handling**: 
    *   `except Exception as e:` and the bare `except:` block are used. This hides potential bugs and makes debugging difficult. Catch specific exceptions (e.g., `sqlite3.Error`).
*   **Deeply Nested Logic**: The query result processing uses deeply nested `if/else` blocks. This increases cognitive load. Use guard clauses or a mapping dictionary to simplify the logic.
*   **Implicit Truthiness**: `if len(r) > 0:` is used. While correct here, prefer explicit checks or iterate directly over the collection.

### 6. Readability & Consistency
*   **Hard-coded Constants**: The database name `"test.db"` is hard-coded. Move this to a configuration constant at the top of the file.
*   **Language Consistency**: The print statements mix English and Chinese (`"找到 Alice"`, `"查詢失敗"`). Use a consistent language for logs/output.