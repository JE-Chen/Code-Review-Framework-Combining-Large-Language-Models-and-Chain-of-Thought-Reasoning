### Diff #1

#### 1. **Summary**
This PR introduces a new Python script `sql_app.py` that handles database operations using SQLite. The script defines a single function `functionThatDoesTooManyThingsAndIsHardToRead()` which connects to a SQLite database, creates a table, inserts data, queries data, and prints results. The function performs all these tasks within a single method, making it difficult to understand and maintain.

#### 2. **Linting Issues**
- **File:** sql_app.py  
  - **Line:** 8  
    - **Issue:** Missing space before colon in class definition.  
    - **Suggestion:** Add a space after `def`.
- **File:** sql_app.py  
  - **Line:** 17  
    - **Issue:** Variable names should be lowercase with underscores.  
    - **Suggestion:** Rename `conn`, `cursorThing` to `connection`, `cursor`.
- **File:** sql_app.py  
  - **Line:** 21  
    - **Issue:** SQL query string contains user-provided values without parameterization.  
    - **Suggestion:** Use parameterized queries to prevent SQL injection.
- **File:** sql_app.py  
  - **Line:** 35  
    - **Issue:** Unnecessary exception handling that ignores errors.  
    - **Suggestion:** Handle exceptions appropriately or rethrow them.
- **File:** sql_app.py  
  - **Line:** 49  
    - **Issue:** Redundant check for `len(r) > 0`.  
    - **Suggestion:** Remove the check since `fetchall()` returns a list of tuples.

#### 3. **Code Smells**
- **Long Function:**  
  - **Issue:** `functionThatDoesTooManyThingsAndIsHardToRead()` has multiple responsibilities including connection management, table creation, data insertion, and querying.  
  - **Recommendation:** Refactor the function into smaller, more focused functions.
- **Poor Naming:**  
  - **Issue:** The function name does not accurately reflect its purpose.  
  - **Recommendation:** Rename to something like `initialize_database_and_operations()`.
- **Tight Coupling:**  
  - **Issue:** Global variables (`conn`, `cursorThing`) are used throughout the function, leading to tight coupling.  
  - **Recommendation:** Pass database connections and cursors as parameters to functions.
- **Inefficient Query Handling:**  
  - **Issue:** Nested conditional statements for printing results.  
  - **Recommendation:** Simplify logic with cleaner control structures.