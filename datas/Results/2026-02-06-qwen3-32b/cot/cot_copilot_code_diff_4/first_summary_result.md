# Code Review Summary

- **Key changes**: Added a new SQLite database script (`sql_app.py`) implementing table creation, data insertion, and query execution in a single function.
- **Impact scope**: Entirely new file `sql_app.py` with database logic and global state management.
- **Purpose of changes**: Intended to demonstrate basic SQLite operations (though implementation has critical flaws).
- **Risks and considerations**: 
  - **Critical security risk**: SQL injection vulnerability from string concatenation in queries (e.g., `name + "..."`).
  - **Poor error handling**: Exceptions are silently ignored (`print` instead of logging/re-raising).
  - **Non-maintainable code**: Monolithic function violates single responsibility principle.
  - **Hard to test**: Global state and tight coupling prevent unit testing.
- **Items to confirm**: 
  - Verify all SQL queries use parameterized syntax (e.g., `cursor.execute("...", (param,))`).
  - Replace global variables (`conn`, `cursorThing`) with function-scoped resources.
  - Split function into discrete units (e.g., `create_table`, `insert_user`, `query_users`).