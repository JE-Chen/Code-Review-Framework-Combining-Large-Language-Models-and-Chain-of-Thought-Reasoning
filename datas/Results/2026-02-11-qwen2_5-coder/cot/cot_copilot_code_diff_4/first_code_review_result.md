- **Code Readability**:
  - **Indentation**: Properly indented.
  - **Formatting**: Good use of whitespace around operators and after commas.
  - **Comments**: Lack of comments explaining the purpose of the code.

- **Naming Conventions**:
  - `conn` and `cursorThing`: Vague names that don't convey their purpose.
  - `functionThatDoesTooManyThingsAndIsHardToRead`: Descriptive but could be more concise.
  - `anotherName`, `anotherAge`: Clear but redundant compared to `name`, `age`.

- **Software Engineering Standards**:
  - Global variables (`conn`, `cursorThing`) used without encapsulation.
  - SQL queries constructed using string concatenation which is prone to SQL injection.
  - No error handling for database operations other than printing messages.

- **Logic & Correctness**:
  - Potential SQL injection vulnerability due to direct string interpolation.
  - Hardcoded database path ("test.db") which might not be desirable in production.
  - Lack of rollback mechanism in case of exceptions during database operations.

- **Performance & Security**:
  - No connection pooling or reuse of connections.
  - Inefficient use of nested conditionals for simple checks.

- **Documentation & Testing**:
  - No docstrings or comments explaining the functionality.
  - Missing unit tests for individual functions.

### Improvement Suggestions

1. **Refactor into Functions**:
   - Split `functionThatDoesTooManyThingsAndIsHardToRead` into smaller functions each doing one thing.

2. **Use Parameterized Queries**:
   - Replace string concatenation with parameterized queries to prevent SQL injection.

3. **Encapsulate Database Operations**:
   - Use context managers to manage database connections automatically.

4. **Add Comments and Docstrings**:
   - Document the purpose of functions and classes.

5. **Unit Tests**:
   - Write unit tests to ensure each function works correctly independently.