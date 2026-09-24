### Code Review

#### 1. Readability & Consistency
- **Formatting:** The code lacks consistent spacing and follows a monolithic structure.
- **Language Consistency:** The print statements mix English and Chinese (`"找到 Alice:"`, `"查詢失敗但我不在乎"`), which should be standardized to one language for professional consistency.

#### 2. Naming Conventions
- **Function Naming:** `functionThatDoesTooManyThingsAndIsHardToRead` is non-descriptive and violates professional naming standards. It should be renamed to reflect its purpose (e.g., `initialize_and_populate_users`).
- **Variable Naming:** `cursorThing` is vague. Use `cursor` or `db_cursor`. `anotherName` and `anotherAge` are generic; use more descriptive names or a data structure.

#### 3. Software Engineering Standards
- **Modularity:** The function violates the Single Responsibility Principle. It handles connection management, table creation, data insertion, and data querying all in one block. These should be split into separate functions (e.g., `setup_db()`, `add_user()`, `query_users()`).
- **Global State:** The use of `global conn, cursorThing` is unnecessary and dangerous for maintainability and thread safety. Pass these as arguments or encapsulate them in a class.

#### 4. Logic & Correctness
- **Exception Handling:** 
    - The `try...except` blocks are too broad. Catching `Exception` or using a bare `except:` hides critical bugs and makes debugging difficult.
    - The error messages (`"Something happened but I will ignore"`) indicate a lack of proper error recovery or logging.
- **Nested Logic:** The `if/else` chain inside the loop is redundant and deeply nested. This can be simplified using a mapping or a more direct conditional.

#### 5. Performance & Security
- **SQL Injection Risk:** **Critical Security Vulnerability.** The code uses string concatenation to build queries:
  `"INSERT INTO users(name, age) VALUES('" + name + "', " + str(age) + ")"`
  This allows for SQL injection. Always use parameterized queries:
  `cursor.execute("INSERT INTO users(name, age) VALUES(?, ?)", (name, age))`
- **Resource Management:** The connection is closed at the end of the function, but if an exception occurs before `conn.close()`, the connection may remain open. Use a `with` statement (context manager) for both the connection and the cursor.

#### 6. Documentation & Testing
- **Documentation:** There are no docstrings or comments explaining the purpose of the script.
- **Testing:** No unit tests are provided to verify the database operations.

---

### Summary of Required Changes
1. **Security:** Replace all string-concatenated SQL queries with parameterized queries.
2. **Refactor:** Break the monolithic function into smaller, single-purpose functions.
3. **Clean up:** Remove global variables and rename functions/variables to be descriptive.
4. **Robustness:** Implement specific exception handling and use context managers (`with sqlite3.connect(...)`).
5. **Consistency:** Standardize the output language to English.