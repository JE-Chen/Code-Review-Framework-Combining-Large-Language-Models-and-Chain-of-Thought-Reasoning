### Code Review

**Naming Conventions**
*   **Function Naming:** `functionThatDoesTooManyThingsAndIsHardToRead` is non-standard and overly verbose. Use a descriptive, concise name (e.g., `initialize_and_populate_users`).
*   **Variable Naming:** `cursorThing` is vague. Use `cursor` to follow standard database naming conventions.
*   **Variable Naming:** `anotherName` and `anotherAge` are generic. Use more descriptive names or a data structure (like a list of tuples) to handle multiple entries.

**Software Engineering Standards**
*   **Modularity:** The function violates the Single Responsibility Principle. It handles connection management, table creation, data insertion, and data querying. Split these into separate functions.
*   **Global State:** Avoid using `global conn, cursorThing`. Pass the connection or cursor as arguments to functions to improve testability and maintainability.

**Logic & Correctness**
*   **SQL Injection Risk:** The code uses string concatenation to build queries (`"VALUES('" + name + ...`). This is a critical security vulnerability. Use parameterized queries (e.g., `cursor.execute("INSERT INTO users(name, age) VALUES(?, ?)", (name, age))`).
*   **Exception Handling:** 
    *   `except Exception as e` and the bare `except:` block are too broad. Catch specific exceptions (e.g., `sqlite3.Error`).
    *   The error messages ("I will ignore", "但我不在乎") are unprofessional and do not provide actionable information for debugging.

**Readability & Consistency**
*   **Nested Logic:** The nested `if/else` blocks for checking "Alice" and "Bob" are redundant and hard to read. Use a flatter structure or a mapping.
*   **Language Consistency:** The print statements mix English and Chinese. Stick to one language for consistency.

**Performance & Security**
*   **Resource Management:** The connection is closed at the end, but if an exception occurs before `conn.close()`, the connection may remain open. Use a `with` statement (context manager) for the connection and cursor.