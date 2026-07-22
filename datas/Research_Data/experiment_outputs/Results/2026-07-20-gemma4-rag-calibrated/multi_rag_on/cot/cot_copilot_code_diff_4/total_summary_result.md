1. **Overall conclusion**
   - The PR does **not** meet merge criteria.
   - There are **blocking critical security vulnerabilities** (SQL Injection) and significant architectural flaws that must be addressed before this code can be merged.

2. **Comprehensive evaluation**
   - **Code Quality and Correctness**: The implementation contains a severe security risk due to the use of string concatenation for SQL queries, making the application vulnerable to SQL injection. Logic is further compromised by improper exception handling, including a bare `except:` block and generic `Exception` catches that silence errors with unprofessional messages.
   - **Maintainability and Design**: The code suffers from poor modularity, with a single "God Function" handling connection, schema creation, data insertion, and querying. The use of `global` variables for database connections creates tight coupling and hinders testability.
   - **Consistency and Standards**: Naming conventions are inconsistent and non-professional (e.g., `functionThatDoesTooManyThingsAndIsHardToRead`, `cursorThing`), violating PEP 8 standards. There is also a lack of consistency in language, mixing English and Chinese in output statements.

3. **Final decision recommendation**
   - **Request changes**
   - **Justification**: The presence of high-priority security vulnerabilities (SQL Injection) and fundamental violations of software engineering principles (SRP, Resource Management, and Error Handling) necessitates a complete refactor.

4. **Team follow-up**
   - **Security**: Replace all string-concatenated SQL queries with parameterized queries.
   - **Refactor**: Decompose the monolithic function into smaller, single-purpose functions (e.g., `init_db`, `add_user`, `fetch_users`).
   - **Resource Management**: Replace manual `conn.close()` and global variables with context managers (`with sqlite3.connect(...)`).
   - **Cleanup**: Rename variables and functions to follow `snake_case` and descriptive naming standards; replace generic `except` blocks with specific `sqlite3.Error` handling.