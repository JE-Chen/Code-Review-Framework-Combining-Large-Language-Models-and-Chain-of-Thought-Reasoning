**Diff #1: sql_app.py**

---

### Summary
This diff introduces a new Python file implementing SQLite database operations. The primary function performs database connection, table creation, data insertion, querying, and cleanup. It handles two hardcoded user records ("Alice" and "Bob") and prints query results. The code is designed as a standalone script (via `if __name__ == "__main__"`), but its monolithic structure and poor practices make it unsuitable for production use. The file focuses on demonstrating basic SQLite interactions without separation of concerns.

---

### Linting Issues
- **Poor variable naming**:  
  `cursorThing` (line 4) violates Python naming conventions (should be `cursor`).  
  *Fix*: Rename to `cursor` for clarity and consistency.
  
- **Global variable misuse**:  
  `global conn, cursorThing` (line 6) is unnecessary and breaks encapsulation.  
  *Fix*: Remove `global` and manage state via function parameters/return values.

- **Inconsistent string formatting**:  
  Hardcoded SQL queries use unsafe string concatenation (e.g., `"'" + name + "'"`).  
  *Fix*: Use parameterized queries (e.g., `cursor.execute("INSERT INTO ...", (name, age))`).

---

### Code Smells
- **Single Responsibility Violation**:  
  `functionThatDoesTooManyThingsAndIsHardToRead` handles connection, schema setup, data insertion, querying, and cleanup.  
  *Why bad*: Makes the function long (25+ lines), error-prone, and impossible to test independently.  
  *Fix*: Split into dedicated functions (e.g., `setup_database()`, `insert_user()`, `query_users()`).

- **SQL Injection Risk**:  
  String concatenation for SQL values (e.g., `"INSERT ... VALUES('" + name + "'..."`) exposes the code to injection attacks.  
  *Why bad*: Even with hardcoded values, this pattern is dangerous and violates security best practices.  
  *Fix*: Always use parameterized queries with `cursor.execute()`.

- **Overly Broad Exception Handling**:  
  `except Exception as e` (line 10) and `except:` (line 27) ignore all errors without context.  
  *Why bad*: Masks critical failures (e.g., connection issues) and hinders debugging.  
  *Fix*: Catch specific exceptions (e.g., `sqlite3.Error`) and log meaningful errors.

- **Hardcoded Logic**:  
  User data ("Alice", "Bob") and query logic are embedded directly in the function.  
  *Why bad*: Prevents reuse and requires code changes for new data.  
  *Fix*: Parameterize user data or add a data source layer.

- **Unnecessary Global State**:  
  `conn` and `cursorThing` are global variables.  
  *Why bad*: Creates hidden dependencies, complicates testing, and risks race conditions.  
  *Fix*: Pass database connections as arguments to functions.