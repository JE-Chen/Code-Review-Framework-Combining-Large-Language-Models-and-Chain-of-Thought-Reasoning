### Code Review

**Naming Conventions**
*   `functionThatDoesTooManyThingsAndIsHardToRead`: Name is overly verbose and describes the problem rather than the purpose. Suggest `setup_and_query_users`.
*   `cursorThing`: Vague naming. Suggest `cursor`.
*   `anotherName` / `anotherAge`: Non-descriptive. Suggest using a list of users and a loop.

**Software Engineering Standards**
*   **Modularity**: The function violates the Single Responsibility Principle by handling connection, table creation, data insertion, and querying in one block. Split these into separate functions.
*   **Global State**: Use of `global conn, cursorThing` is unnecessary and makes the code harder to test and maintain. Pass these as arguments or encapsulate them in a class.

**Logic & Correctness**
*   **SQL Injection**: Using string concatenation for queries (`"VALUES('" + name + ...`) is a critical security risk. Use parameterized queries: `cursor.execute("INSERT INTO users(name, age) VALUES(?, ?)", (name, age))`.
*   **Exception Handling**: 
    *   `except Exception as e` and the bare `except:` block are too broad. Catch specific exceptions (e.g., `sqlite3.Error`).
    *   Printing "I will ignore" or "I don't care" is not appropriate for production error handling.

**Readability & Consistency**
*   **Nested Logic**: The nested `if/else` blocks for printing user names are redundant. Use a dictionary or a more streamlined conditional structure.
*   **Language Consistency**: Mixing English and Chinese in print statements (`找到 Alice` vs `Something happened`) reduces codebase consistency.

**Performance & Security**
*   **Resource Management**: The connection is closed at the end, but if an exception occurs before `conn.close()`, the connection may remain open. Use a `with` statement (context manager) for the connection.