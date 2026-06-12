### Code Review Report

#### 1. Readability & Consistency
* **Mixed Language:** The `print` statements use a mix of English and Chinese. Maintain a consistent language for logs and output.
* **Deep Nesting:** The `if/else` block inside the `for` loop is unnecessarily deep, reducing readability.

#### 2. Naming Conventions
* **Function Naming:** `functionThatDoesTooManyThingsAndIsHardToRead` is non-standard and unprofessional. Use a descriptive name like `initialize_and_query_users`.
* **Variable Naming:** `cursorThing` is vague. Use standard naming such as `cursor`.
* **Naming Style:** `anotherName` and `anotherAge` use camelCase, which deviates from the Python PEP 8 standard (snake_case).

#### 3. Software Engineering Standards
* **Global State:** The use of `global conn, cursorThing` is a poor practice. Pass these objects as arguments or encapsulate them within a class/context manager.
* **Lack of Modularity:** The function handles connection, table creation, data insertion, and querying. These should be split into separate functions (e.g., `create_table()`, `add_user()`, `get_users()`).
* **Resource Management:** Database connections should be handled using `with` statements (context managers) to ensure they close properly even if an error occurs.

#### 4. Logic & Correctness
* **Bare Except Blocks:** `except:` and `except Exception as e:` are used with prints that "ignore" the error. This hides critical failures and makes debugging difficult.
* **Redundant Check:** `if len(r) > 0:` is redundant as `fetchall()` returns rows that will contain data if the query succeeded.

#### 5. Performance & Security
* **SQL Injection Risk:** **Critical Issue.** The code uses string concatenation to build queries (`VALUES('" + name + ...`). This is highly vulnerable to SQL injection. Use parameterized queries: `cursor.execute("INSERT INTO users(name, age) VALUES(?, ?)", (name, age))`.

#### 6. Documentation & Testing
* **Missing Docs:** There are no docstrings or comments explaining the purpose of the script.
* **No Tests:** No unit tests are provided to verify the logic.

---

### Summary of Suggestions
* **Refactor** the large function into smaller, single-purpose functions.
* **Replace** string concatenation in SQL queries with parameterized inputs immediately.
* **Remove** global variables and use context managers (`with sqlite3.connect(...)`).
* **Rename** variables and functions to follow PEP 8 (snake_case) and be descriptive.
* **Implement** proper error handling instead of ignoring exceptions.