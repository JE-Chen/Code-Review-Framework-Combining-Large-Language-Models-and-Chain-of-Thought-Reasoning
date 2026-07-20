### Code Review

**Naming Conventions**
*   `functionThatDoesTooMuchAndIsHardToUnderstand`: Use `snake_case` for Python functions and provide a descriptive name that reflects the function's purpose.
*   `weirdVariableName`: Use a descriptive name (e.g., `post_response`) instead of a vague placeholder.
*   `r2`: Use a more meaningful name (e.g., `posts_response`).

**Software Engineering Standards**
*   **Modularity**: The function violates the Single Responsibility Principle by performing multiple unrelated GET and POST requests. Split these into smaller, focused functions.
*   **Shared Mutable State**: `GLOBAL_SESSION` is used as a global mutable object. Pass the session as an argument to functions to improve testability and avoid hidden coupling.

**Logic & Correctness**
*   **Broad Exception Handling**: 
    *   `except Exception as e:` is too broad. Catch specific `requests` exceptions (e.g., `requests.RequestException`).
    *   The bare `except:` block is highly discouraged as it catches all exceptions, including `SystemExit` and `KeyboardInterrupt`.

**Readability & Consistency**
*   **Mixed Languages**: The print statements use a mix of Chinese and English. Use a consistent language for logs/output.
*   **Formatting**: The `GLOBAL_SESSION.post` call is slightly inconsistently indented.

**Performance & Security**
*   **Resource Management**: While a session is used, there is no mechanism to ensure the session is closed (e.g., using a context manager or a cleanup function).