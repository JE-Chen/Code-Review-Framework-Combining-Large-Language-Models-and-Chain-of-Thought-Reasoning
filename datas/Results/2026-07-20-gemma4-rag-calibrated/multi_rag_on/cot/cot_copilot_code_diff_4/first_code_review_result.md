### Code Review

**Naming Conventions**
* `functionThatDoesTooManyThingsAndIsHardToRead`: Name is overly verbose and describes the problem rather than the purpose. Suggest `initialize_and_populate_users`.
* `cursorThing`: Vague naming. Suggest `cursor`.
* `anotherName` / `anotherAge`: Non-descriptive. Suggest using a list of user data and a loop.

**Software Engineering Standards**
* **Modularity**: The function violates the Single Responsibility Principle. It handles connection management, table creation, data insertion, and data querying. These should be split into separate functions.
* **Global State**: Use of `global conn, cursorThing` is unnecessary and makes the code harder to test and maintain. Pass connections as arguments or use a context manager.

**Logic & Correctness**
* **SQL Injection**: The code uses string concatenation to build queries (`"VALUES('" + name + ...`). This is a critical security risk. Use parameterized queries: `cursor.execute("INSERT INTO users(name, age) VALUES(?, ?)", (name, age))`.
* **Exception Handling**: 
    * `except Exception as e` and the bare `except:` block are too broad. Catch specific exceptions (e.g., `sqlite3.Error`).
    * Printing "I will ignore" or "I don't care" is not appropriate for production error handling.

**Readability & Consistency**
* **Nested Logic**: The nested `if/else` blocks for checking "Alice" and "Bob" are redundant. Use a flatter structure or a mapping.
* **Consistency**: Mixing English and Chinese in print statements reduces codebase consistency.

**Performance & Security**
* **Resource Management**: The connection is closed at the end, but if an exception occurs before `conn.close()`, the connection may remain open. Use a `with sqlite3.connect(...) as conn:` block to ensure resources are released.