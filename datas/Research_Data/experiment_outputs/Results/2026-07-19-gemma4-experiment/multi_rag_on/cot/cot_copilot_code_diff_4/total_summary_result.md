1. **Overall conclusion**
   - The PR does **not** meet merge criteria.
   - There are **blocking critical concerns** regarding security (SQL injection) and stability (improper exception handling).
   - Significant refactoring is required to address architectural flaws and naming violations.

2. **Comprehensive evaluation**
   - **Code Quality and Correctness:** The code contains a critical security vulnerability due to the use of string concatenation for SQL queries, making it susceptible to SQL injection. Logic is further compromised by broad `except` blocks and a bare `except:` clause that mask errors and prevent proper debugging.
   - **Maintainability and Design:** The design violates the Single Responsibility Principle; a single monolithic function handles connection, schema creation, data insertion, and querying. The use of `global` variables for database state creates tight coupling and hinders testability.
   - **Consistency:** Naming is inconsistent and non-semantic (e.g., `cursorThing`, `functionThatDoesTooManyThingsAndIsHardToRead`). There is also a lack of linguistic consistency, mixing English and Chinese in output statements.

3. **Final decision recommendation**
   - **Request changes**
   - **Justification:** The presence of high-priority security risks (SQL injection) and poor software engineering practices (global state, SRP violation, and silent failure patterns) necessitates a complete rewrite of the logic before it can be safely merged.

4. **Team follow-up**
   - **Security:** Replace all string-concatenated queries with parameterized queries.
   - **Refactor:** Decompose the monolithic function into modular components (e.g., `init_db`, `add_user`, `query_users`).
   - **Resource Management:** Implement context managers (`with` statements) for database connections and cursors to ensure resources are closed during exceptions.
   - **Cleanup:** Rename variables and functions to follow `snake_case` and descriptive naming standards; standardize all print/log messages to a single language.
   - **Error Handling:** Replace generic `Exception` and bare `except` blocks with specific `sqlite3.Error` handling.