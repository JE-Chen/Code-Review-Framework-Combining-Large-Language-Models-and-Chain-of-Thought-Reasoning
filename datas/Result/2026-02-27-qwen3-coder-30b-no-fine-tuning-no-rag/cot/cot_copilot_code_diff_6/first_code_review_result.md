- **Readability & Consistency**:
  - Indentation is consistent, but comments are in Chinese and could be improved for international collaboration.
  - No clear formatting style (e.g., spacing around operators) — consider using a linter like `black` or `flake8`.

- **Naming Conventions**:
  - Function name `functionThatDoesTooMuchAndIsHardToUnderstand()` is too verbose and unclear; it should reflect a single responsibility.
  - Variables like `weirdVariableName` and `r2` lack descriptive meaning.
  - Global constants such as `ANOTHER_GLOBAL` should follow `UPPER_CASE` convention.

- **Software Engineering Standards**:
  - The function performs multiple responsibilities (GET, POST, logging), violating the Single Responsibility Principle.
  - Duplicate error handling logic exists for similar operations.
  - Use of global variables (`GLOBAL_SESSION`) makes code harder to test and maintain.

- **Logic & Correctness**:
  - Broad exception handling (`except:`) masks potential issues without proper logging or re-raising.
  - Lack of status code checks after POST request may lead to unexpected behavior.
  - No return values or structured output, making the function non-reusable.

- **Performance & Security**:
  - No timeout set on requests, risking hanging connections.
  - Hardcoded URLs and data reduce flexibility and introduce security risk if used in production.

- **Documentation & Testing**:
  - Missing docstrings or inline comments explaining purpose or parameters.
  - No unit tests provided; testing is needed for reliability and future changes.

- **Suggestions**:
  - Refactor into smaller functions with specific tasks.
  - Replace broad `except:` with specific exception types.
  - Add timeouts and proper error logging.
  - Rename variables and functions for clarity.
  - Move globals to a configuration module or pass as arguments.