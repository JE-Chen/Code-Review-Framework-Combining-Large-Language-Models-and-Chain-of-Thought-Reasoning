Here's a concise code review focusing on the most critical issues:

- **Naming Conventions**:  
  `cursorThing` is unclear and unprofessional (use `cursor` instead).  
  Function name `functionThatDoesTooManyThingsAndIsHardToRead()` violates descriptive naming rules.

- **Security Risk**:  
  String concatenation in SQL queries (`"VALUES('" + name + "'..."`) creates **SQL injection vulnerability**. Always use parameterized queries.

- **Error Handling**:  
  Ignoring exceptions (`except Exception as e: print(...)` and `except: print(...)`) masks failures. Handle errors explicitly or log them.

- **Code Clarity**:  
  Redundant checks (`if len(r) > 0`) and nested conditionals (`if r[1] == "Alice": ... else: ...`) reduce readability.  
  Variables like `anotherName`/`anotherAge` are ambiguous.

- **Single Responsibility Violation**:  
  Function handles DB setup, inserts, and query logic. Split into focused units (e.g., `create_table()`, `insert_user()`, `query_users()`).

- **Brittleness**:  
  Hardcoded column indices (`r[1]`) fail if schema changes. Use named tuples or column names.

- **Global Variables**:  
  Unnecessary `global conn, cursorThing` pollutes scope. Manage DB connections locally.

**Improvement Suggestions**:
1. Replace string-based SQL with parameterized queries (e.g., `cursor.execute("INSERT INTO users VALUES(?, ?, ?)", (None, name, age))`).
2. Rename function to `setup_database_and_query` (or split into smaller functions).
3. Remove redundant `if len(r) > 0` checks.
4. Add error logging (e.g., `logger.error(...)`) instead of silent ignores.
5. Use descriptive variables (`user_name`, `user_age` instead of `name`, `anotherName`).