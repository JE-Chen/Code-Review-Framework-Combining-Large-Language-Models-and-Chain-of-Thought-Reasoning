### Code Review

**Naming Conventions**
*   **Function Naming:** `functionThatDoesTooManyThingsAndIsHardToRead` is non-descriptive and violates professional naming standards. Rename to something reflecting its purpose (e.g., `initialize_and_populate_users`).
*   **Variable Naming:** `cursorThing` is vague. Use `cursor`.
*   **Consistency:** Mix of `name`/`age` and `anotherName`/`anotherAge` is redundant. Use a loop or a data structure.

**Software Engineering Standards**
*   **Modularity:** The function violates the Single Responsibility Principle. It handles connection management, table creation, data insertion, and data querying. These should be split into separate functions.
*   **Global State:** Use of `global conn, cursorThing` is unnecessary and makes the code harder to test and maintain. Pass these as arguments or encapsulate them in a class.

**Logic & Correctness**
*   **Security (SQL Injection):** The code uses string concatenation to build queries (`"VALUES('" + name + ...`). This is a critical security vulnerability. Use parameterized queries: `cursor.execute("INSERT INTO users(name, age) VALUES(?, ?)", (name, age))`.
*   **Exception Handling:** 
    *   `except Exception as e` and the bare `except:` block are too broad. Catch specific exceptions (e.g., `sqlite3.Error`).
    *   The error messages are unprofessional and do not provide actionable information.

**Readability & Consistency**
*   **Nested Logic:** The nested `if/else` blocks for checking "Alice" and "Bob" are redundant and deep. Use a flatter structure or a mapping.
*   **Language Consistency:** Print statements mix English and Chinese, which should be standardized based on the project's locale.

**Performance & Security**
*   **Resource Management:** The connection is closed at the end, but if an exception occurs before `conn.close()`, the connection may remain open. Use a `with` statement (context manager) for the connection.