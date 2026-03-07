### Code Smell Type: Global State Usage
- **Problem Location:** `global conn, cursorThing` in `functionThatDoesTooManyThingsAndIsHardToRead()`
- **Detailed Explanation:** The use of global variables (`conn`, `cursorThing`) makes the function tightly coupled to the global state, which reduces modularity, readability, and testability. It also introduces side effects that are hard to track and debug. This pattern increases the risk of unintended interactions between functions and makes the code harder to reason about.
- **Improvement Suggestions:** Replace global variables with local parameters or return values. Consider encapsulating database operations into a dedicated class with proper initialization and cleanup methods.
- **Priority Level:** High

---

### Code Smell Type: Function with Multiple Responsibilities (Violation of Single Responsibility Principle)
- **Problem Location:** `functionThatDoesTooManyThingsAndIsHardToRead()` 
- **Detailed Explanation:** This function performs multiple unrelated tasks such as connecting to a database, creating a table, inserting data, querying data, and printing results. A function should have one clear responsibility to improve maintainability and testability. This violates the Single Responsibility Principle.
- **Improvement Suggestions:** Break down this monolithic function into smaller, focused functions (e.g., `create_table()`, `insert_user()`, `fetch_users()`, `print_results()`). Each should handle a single task.
- **Priority Level:** High

---

### Code Smell Type: Magic Strings
- **Problem Location:** `"CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, name TEXT, age INTEGER)"` and similar SQL queries
- **Detailed Explanation:** Hardcoded strings like SQL commands make the code less readable and more error-prone. If these strings need to change, they must be updated in multiple places. Additionally, using string concatenation for SQL queries exposes the application to SQL injection attacks.
- **Improvement Suggestions:** Use parameterized queries instead of string concatenation. Store frequently used strings in constants or configuration files if needed.
- **Priority Level:** High

---

### Code Smell Type: Insecure SQL Query Construction
- **Problem Location:** String concatenation in SQL statements:
  ```python
  cursorThing.execute("INSERT INTO users(name, age) VALUES('" + name + "', " + str(age) + ")")
  ```
- **Detailed Explanation:** Concatenating user inputs directly into SQL queries without sanitization or parameterization leads to serious vulnerabilities like SQL injection. Even though this is a simple example, it demonstrates poor practice that can lead to data breaches or unauthorized access.
- **Improvement Suggestions:** Use parameterized queries to safely insert values into the database:
  ```python
  cursorThing.execute("INSERT INTO users(name, age) VALUES(?, ?)", (name, age))
  ```
- **Priority Level:** High

---

### Code Smell Type: Poor Error Handling
- **Problem Location:** Catch-all exceptions with generic messages:
  ```python
  except Exception as e:
      print("Something happened but I will ignore:", e)
  ...
  except:
      print("查詢失敗但我不在乎")
  ```
- **Detailed Explanation:** Using broad exception handlers prevents proper error logging or handling. Ignoring exceptions hides potential issues from developers and users. This makes debugging difficult and can mask real problems.
- **Improvement Suggestions:** Catch specific exceptions where possible and log them appropriately rather than ignoring them. Use structured logging for better diagnostics.
- **Priority Level:** Medium

---

### Code Smell Type: Lack of Input Validation
- **Problem Location:** No validation on input data before insertion
- **Detailed Explanation:** There's no check for valid types or ranges of `name` and `age`. For instance, passing invalid data could corrupt the database or cause unexpected behavior.
- **Improvement Suggestions:** Add validation checks for inputs, especially when dealing with external or untrusted data sources.
- **Priority Level:** Medium

---

### Code Smell Type: Unclear Naming Convention
- **Problem Location:** Function name `functionThatDoesTooManyThingsAndIsHardToRead()` and variable names like `cursorThing`
- **Detailed Explanation:** Descriptive and meaningful names are crucial for code comprehension. The current naming convention does not reflect the purpose of the function or variables, making it hard to understand at first glance.
- **Improvement Suggestions:** Rename `functionThatDoesTooManyThingsAndIsHardToRead()` to something like `setup_and_query_database()`. Rename `cursorThing` to `cursor`.
- **Priority Level:** Medium

---

### Code Smell Type: Duplicated Logic
- **Problem Location:** Similar conditional logic inside the loop:
  ```python
  if r[1] == "Alice":
      print("找到 Alice:", r)
  else:
      if r[1] == "Bob":
          print("找到 Bob:", r)
      else:
          print("其他人:", r)
  ```
- **Detailed Explanation:** Repetitive conditional blocks reduce readability and increase the chance of errors during future modifications. It also violates the DRY (Don’t Repeat Yourself) principle.
- **Improvement Suggestions:** Refactor this logic into a lookup dictionary or switch-case equivalent structure for cleaner control flow.
- **Priority Level:** Medium

---

### Code Smell Type: Missing Resource Management Best Practices
- **Problem Location:** Manual `commit()` and `close()` calls
- **Detailed Explanation:** While the code closes the connection after usage, relying on manual resource management increases the risk of resource leaks if an exception occurs before closing. Using context managers ensures safe resource handling.
- **Improvement Suggestions:** Wrap database connections in a context manager (`with` statement) to ensure automatic closing even in case of failure.
- **Priority Level:** Medium

---

### Code Smell Type: Hardcoded Database Path
- **Problem Location:** `"test.db"` in `sqlite3.connect("test.db")`
- **Detailed Explanation:** Hardcoding the path to the database file reduces flexibility and makes deployment harder. It also makes testing more complex since different environments might require different paths.
- **Improvement Suggestions:** Move hardcoded paths to environment variables or configuration settings so that configurations can vary per environment.
- **Priority Level:** Low

---

### Summary of Improvements:
1. Eliminate global state by using classes or modules.
2. Split large functions into smaller, single-responsibility ones.
3. Use parameterized queries to prevent SQL injection.
4. Improve naming conventions to enhance clarity.
5. Handle exceptions properly with logging.
6. Apply resource management patterns (context managers).
7. Avoid magic strings and hardcodes via constants/configurations.
8. Refactor repetitive logic for better maintainability.