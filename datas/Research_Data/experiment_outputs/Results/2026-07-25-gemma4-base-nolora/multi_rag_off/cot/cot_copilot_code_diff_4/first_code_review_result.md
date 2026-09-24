### Code Review

**Naming Conventions**
* **Function Naming:** `functionThatDoesTooManyThingsAndIsHardToRead` is non-descriptive and violates professional naming standards. Rename to something reflecting its purpose (e.g., `initialize_and_populate_users`).
* **Variable Naming:** `cursorThing` is vague. Use `cursor`.
* **Consistency:** Use `snake_case` for variables (e.g., `another_name` instead of `anotherName`) to adhere to PEP 8 standards.

**Software Engineering Standards**
* **Modularity:** The function violates the Single Responsibility Principle. It handles connection management, table creation, data insertion, and data querying. These should be split into separate functions.
* **Global State:** The use of `global conn, cursorThing` is unnecessary and makes the code harder to test and maintain. Pass these as arguments or encapsulate them in a class.

**Logic & Correctness**
* **Security (SQL Injection):** The code uses string concatenation to build queries: `VALUES('" + name + "', ...)`. This is a critical security vulnerability. Use parameterized queries: `cursor.execute("INSERT INTO users(name, age) VALUES(?, ?)", (name, age))`.
* **Exception Handling:** 
    * `except Exception as e` and the bare `except:` block are too broad. Catch specific exceptions (e.g., `sqlite3.Error`).
    * Printing "I will ignore" or "I don't care" in logs is unprofessional and hinders debugging.

**Readability & Consistency**
* **Nested Logic:** The nested `if/else` blocks for checking "Alice" and "Bob" are redundant. Use a flatter structure or a mapping.
* **Language Consistency:** The print statements mix English and Chinese; stick to one language for consistency.

**Performance & Security**
* **Resource Management:** The connection is closed at the end, but if an exception occurs before `conn.close()`, the connection may remain open. Use a `with` statement (context manager) for both the connection and the cursor.