1. **Overall conclusion**
   - The PR does **not** meet merge criteria.
   - There are **blocking critical concerns** regarding security (SQL injection) and software engineering standards (Single Responsibility Principle).
   - Non-blocking concerns include poor naming conventions, unprofessional error handling, and lack of testing/documentation.

2. **Comprehensive evaluation**
   - **Code Quality and Correctness**: The implementation contains a severe security vulnerability due to the use of string concatenation for SQL queries, making the application susceptible to SQL injection. Logic is further compromised by overly broad exception handling (including a bare `except` block) and unprofessional error messages that mask failures.
   - **Maintainability and Design**: The design is poor, featuring a "God Function" that handles connection, schema creation, data insertion, and querying in a single block. The use of `global` state for database connections hinders testability and thread safety.
   - **Consistency**: The code lacks consistency in naming (mixing `snake_case` and `camelCase`) and language (mixing English and Chinese in print statements).

3. **Final decision recommendation**
   - **Request changes**
   - **Justification**: The PR introduces a critical security risk (SQL injection) and violates fundamental software engineering principles (SRP, global state). These must be resolved before the code can be safely merged.

4. **Team follow-up**
   - **Security**: Replace all string-concatenated SQL queries with parameterized queries.
   - **Refactoring**: Decompose `functionThatDoesTooManyThingsAndIsHardToRead` into modular functions (e.g., `init_db`, `add_user`, `fetch_users`) and remove `global` variables.
   - **Error Handling**: Replace broad `except` blocks with specific `sqlite3.Error` handling and professional logging.
   - **Cleanup**: Standardize naming to `snake_case` and unify the output language.
   - **Testing**: Implement unit tests to verify database operations.