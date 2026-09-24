### Pull Request Summary

*   **Key changes**: Introduced `bad_requests.py` which implements basic GET and POST requests using a global `requests.Session`.
*   **Purpose of changes**: Initial implementation of API interaction logic.
*   **Items to confirm**: Review the error handling and naming conventions as they currently deviate from standard practices.

---

### Code Review

#### 1. Readability & Consistency
*   **Naming Conventions**: The function name `functionThatDoesTooMuchAndIsHardToUnderstand` and variable `weirdVariableName` violate standard Python naming conventions (PEP 8). They should use `snake_case` and be descriptive of their actual purpose (e.g., `fetch_post_data`).
*   **Formatting**: The indentation is generally correct, but the naming makes the code difficult to maintain.

#### 2. Software Engineering Standards
*   **Modularity**: The function violates the Single Responsibility Principle. It performs multiple unrelated network requests (GET for a single item, GET for a list, and a POST request) in one block. This should be refactored into smaller, reusable functions.
*   **Testability**: The code is difficult to unit test because it relies on a global session and hardcoded URLs. Dependencies should be injected (e.g., passing the session as an argument).

#### 3. Logic & Correctness
*   **Exception Handling**: 
    *   The first `try-except` block catches `Exception`, which is too broad.
    *   The second `try-except` block uses a bare `except:`, which is strongly discouraged as it catches `SystemExit` and `KeyboardInterrupt`.
    *   Both blocks simply print the error without proper logging or recovery logic.

#### 4. Performance & Security
*   **Shared Mutable State**: The use of `GLOBAL_SESSION` at the module level introduces shared mutable state. While `requests.Session` is often used for connection pooling, managing it as a global variable can lead to hidden coupling and issues in multi-threaded environments.

#### 5. RAG Rule Violations
*   **Broad Exceptions**: Violated. The code uses `except Exception as e:` and a bare `except:`. Specific exceptions (e.g., `requests.exceptions.RequestException`) should be caught instead.
*   **Shared Mutable State**: Violated. `GLOBAL_SESSION` is a module-level mutable object.
*   **Naming/Clarity**: The function name explicitly admits to being "hard to understand," which contradicts the goal of maintainable code.

### Summary of Required Changes
1.  **Refactor** the large function into smaller, focused functions.
2.  **Rename** functions and variables to follow `snake_case` and be semantically meaningful.
3.  **Replace** broad `except` blocks with specific `requests` exceptions.
4.  **Remove** global state; pass the session object as a parameter to functions.