### Code Review

**Naming Conventions**
*   **Non-descriptive naming:** `functionThatDoesTooManyThingsAndIsHardToRead` and `cursorThing` are unprofessional and vague. Use descriptive names like `initialize_database` or `db_cursor`.
*   **Inconsistent casing:** `anotherName` and `anotherAge` use camelCase, which violates PEP 8 (Python's standard naming convention of `snake_case` for variables).

**Software Engineering Standards**
*   **Lack of Modularity:** The main function violates the Single Responsibility Principle. It handles connection management, table creation, data insertion, and data querying all in one block. These should be split into separate functions.
*   **Global State:** The use of `global conn, cursorThing` is unnecessary and makes the code harder to test and maintain. Pass these as arguments or encapsulate them in a class.

**Logic & Correctness**
*   **SQL Injection Vulnerability:** The code uses string concatenation to build queries (e.g., `VALUES('" + name + "', ...)`). This is a critical security risk. Use parameterized queries: `cursor.execute("INSERT INTO users(name, age) VALUES(?, ?)", (name, age))`.
*   **Fragile Logic:** The nested `if/else` block for printing users is redundant and hard to scale. A simple mapping or a more generic print statement would be more efficient.

**Performance & Security**
*   **Resource Management:** The database connection is closed at the end of the function, but if an exception occurs before `conn.close()`, the connection may remain open. Use a `with` statement (context manager) for both the connection and the cursor.

**Documentation & Testing**
*   **Poor Exception Handling:** `except Exception as e` and the bare `except:` block are too broad. They swallow errors and provide unhelpful print statements ("I will ignore", "I don't care"), which makes debugging nearly impossible.
*   **Missing Documentation:** There are no docstrings or comments explaining the purpose of the script.

**Suggested Improvements**
*   Refactor the logic into `create_table()`, `insert_user()`, and `query_users()` functions.
*   Replace string formatting in SQL with parameters `?`.
*   Replace global variables with a context manager (`with sqlite3.connect(...) as conn:`).
*   Update naming to follow PEP 8 (`snake_case`).