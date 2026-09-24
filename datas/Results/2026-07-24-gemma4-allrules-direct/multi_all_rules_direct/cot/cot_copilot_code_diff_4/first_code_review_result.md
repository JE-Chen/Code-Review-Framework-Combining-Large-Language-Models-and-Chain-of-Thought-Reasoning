### Code Review

**Naming Conventions**
*   **Vague/Non-descriptive Naming**: `functionThatDoesTooManyThingsAndIsHardToRead` and `cursorThing` are not professional or descriptive. Use names that reflect the actual purpose (e.g., `initialize_user_database` and `cursor`).
*   **Inconsistent Casing**: `anotherName` and `anotherAge` use camelCase, which deviates from the Python standard (snake_case).

**Software Engineering Standards**
*   **Single Responsibility Principle**: The function handles database connection, table creation, data insertion, and data querying all in one block. These should be split into smaller, focused functions.
*   **Shared Mutable State**: The use of `global conn, cursorThing` introduces hidden coupling and makes the code harder to test and maintain. Pass these as arguments or encapsulate them in a class.

**Logic & Correctness**
*   **SQL Injection Risk**: Using string concatenation (`"VALUES('" + name + ...`) to build queries is a critical security vulnerability. Use parameterized queries (e.g., `cursor.execute("INSERT INTO users(name, age) VALUES(?, ?)", (name, age))`).
*   **Deeply Nested Logic**: The nested `if/else` block inside the loop increases cognitive load. Use a flatter structure or a mapping.

**Performance & Security**
*   **Resource Management**: The connection is closed at the end, but if an exception occurs before `conn.close()`, the connection may remain open. Use a `with` statement (context manager) for the connection.

**Error Handling**
*   **Broad Exception Catching**: `except Exception as e:` and the bare `except:` block hide potential bugs and make debugging difficult. Catch specific exceptions (e.g., `sqlite3.Error`).
*   **Silent Failures**: Printing "I will ignore" or "I don't care" in exception blocks is not an acceptable error-handling strategy for production code.

**Readability & Consistency**
*   **Mixed Languages**: The print statements use a mix of English and Chinese, which reduces consistency. Stick to one language for logs/output.