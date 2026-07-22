### PR Summary

*   **Key changes**: Introduced `sql_app.py` to handle basic SQLite database operations (table creation, data insertion, and querying).
*   **Impact scope**: New standalone module `sql_app.py`.
*   **Purpose of changes**: Initial implementation of user data persistence.
*   **Items to confirm**: Review the security of SQL execution and the overall structure of the database logic.

---

### Code Review

#### 1. Readability & Consistency
*   **Formatting**: The nested `if/else` blocks in the query loop are unnecessarily deep, reducing readability.
*   **Language Consistency**: The print statements mix English and Chinese (`"找到 Alice:"`, `"查詢失敗但我不在乎"`). Please stick to one language for logs/output.

#### 2. Naming Conventions
*   **Function Naming**: `functionThatDoesTooManyThingsAndIsHardToRead` is non-professional and overly verbose. It should be renamed to reflect its actual purpose (e.g., `initialize_and_query_users`).
*   **Variable Naming**: 
    *   `cursorThing` is vague. Use `cursor`.
    *   `anotherName` and `anotherAge` are generic. Use descriptive names or a loop/list for multiple entries.

#### 3. Software Engineering Standards
*   **Modularity**: The function violates the Single Responsibility Principle. It handles connection management, schema creation, data insertion, and data reporting all in one block. These should be split into separate functions (e.g., `setup_db()`, `add_user()`, `get_users()`).
*   **Global State**: The use of `global conn, cursorThing` is unnecessary and dangerous for maintainability and thread safety. Pass these as arguments or encapsulate them in a class.

#### 4. Logic & Correctness
*   **Exception Handling**: 
    *   The `try...except` blocks are too broad. Catching `Exception` or using a bare `except:` hides critical bugs and makes debugging difficult.
    *   The error messages (`"I will ignore"`, `"I don't care"`) are unprofessional and indicate a lack of proper error recovery or logging.

#### 5. Performance & Security
*   **Critical Security Risk (SQL Injection)**: The code uses string concatenation to build queries:
    `"INSERT INTO users(name, age) VALUES('" + name + "', " + str(age) + ")"`
    **This is a severe security vulnerability.** Always use parameterized queries to prevent SQL injection:
    `cursor.execute("INSERT INTO users(name, age) VALUES(?, ?)", (name, age))`

#### 6. Documentation & Testing
*   **Documentation**: There are no docstrings or comments explaining the purpose of the script or the expected database schema.
*   **Testing**: No unit tests are provided to verify that users are correctly inserted or retrieved.