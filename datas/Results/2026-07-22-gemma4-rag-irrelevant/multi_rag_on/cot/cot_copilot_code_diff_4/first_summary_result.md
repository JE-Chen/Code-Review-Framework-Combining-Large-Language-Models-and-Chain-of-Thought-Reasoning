Here is the code review for `sql_app.py` based on the provided global rules.

### 1. Readability & Consistency
- **Formatting:** The code lacks consistent spacing and structure.
- **Language Consistency:** The print statements mix English and Chinese (`"找到 Alice:"`, `"查詢失敗但我不在乎"`), which should be standardized to one language for professional consistency.

### 2. Naming Conventions
- **Function Naming:** `functionThatDoesTooManyThingsAndIsHardToRead` is non-descriptive and violates professional naming standards. It should be renamed to reflect its purpose (e.g., `initialize_and_populate_users`).
- **Variable Naming:** `cursorThing` is vague. Use `cursor` or `db_cursor`.
- **Case Consistency:** The code mixes `snake_case` (standard for Python) with `camelCase` (`anotherName`, `anotherAge`). All variables should follow `snake_case`.

### 3. Software Engineering Standards
- **Modularity:** The function violates the Single Responsibility Principle. It handles connection management, table creation, data insertion, and data querying all in one block. These should be split into separate functions (e.g., `get_connection()`, `create_table()`, `insert_user()`).
- **Global State:** The use of `global conn, cursorThing` is unnecessary and dangerous, as it makes the code harder to test and prone to side effects. Pass these as arguments or encapsulate them in a class.
- **Code Duplication:** The `INSERT` logic is repeated twice. This should be abstracted into a function that accepts `name` and `age` as parameters.

### 4. Logic & Correctness
- **Exception Handling:** 
    - The `try...except` blocks are too broad. Catching `Exception` or using a bare `except:` hides critical bugs and makes debugging difficult.
    - The error messages (`"I will ignore"`, `"I don't care"`) are unprofessional and indicate a lack of proper error recovery or logging.
- **Resource Management:** If an exception occurs during the `try` blocks, `conn.close()` may be skipped if the exception is not handled correctly. Use a `with` statement (context manager) for the connection and cursor to ensure resources are closed automatically.

### 5. Performance & Security
- **SQL Injection Risk:** **Critical Security Flaw.** The code uses string concatenation to build queries:
  `"INSERT INTO users(name, age) VALUES('" + name + "', " + str(age) + ")"`
  This is highly vulnerable to SQL injection. Always use parameterized queries:
  `cursor.execute("INSERT INTO users(name, age) VALUES(?, ?)", (name, age))`

### 6. Documentation & Testing
- **Documentation:** There are no docstrings or comments explaining the purpose of the script.
- **Testing:** No unit tests are provided to verify the database operations.

---

### Summary of Recommendations
1. **Security:** Immediately switch to parameterized queries to prevent SQL injection.
2. **Refactor:** Break the monolithic function into smaller, reusable functions.
3. **Cleanup:** Remove global variables and standardize naming to `snake_case`.
4. **Robustness:** Implement specific exception handling and use context managers (`with sqlite3.connect(...)`).