### Pull Request Summary

*   **Key changes**: Introduced a new module `bad_requests.py` that performs GET and POST requests to a placeholder API.
*   **Purpose of changes**: Initial implementation of API interaction logic.
*   **Items to confirm**: The current implementation contains several architectural and stylistic issues that require refactoring before merging.

---

### Code Review

#### 1. Readability & Consistency
*   **Naming Conventions**: The function name `functionThatDoesTooMuchAndIsHardToUnderstand` and variable `weirdVariableName` violate standard Python naming conventions (PEP 8) and are not descriptive of the business logic. Use `snake_case` for functions and variables.

#### 2. Software Engineering Standards
*   **Single Responsibility Principle**: The function `functionThatDoesTooMuchAndIsHardToUnderstand` violates the RAG rule regarding single responsibility. It handles multiple distinct API calls (GET single post, GET all posts, POST new post) and performs I/O (printing) simultaneously. These should be split into smaller, focused functions.
*   **Modularization**: The code relies on global state (`GLOBAL_SESSION`), which makes the logic harder to test and reuse.

#### 3. Logic & Correctness
*   **Exception Handling**: 
    *   The code uses `except Exception as e:` and a bare `except:`, which violates the RAG rule against catching broad exceptions. This can hide critical bugs (e.g., `KeyboardInterrupt` or `MemoryError`).
    *   Catch specific exceptions such as `requests.exceptions.RequestException`.

#### 4. Performance & Security
*   **Shared Mutable State**: The use of `GLOBAL_SESSION` at the module level introduces shared mutable state. While `requests.Session` is generally thread-safe for basic use, relying on globals makes the code brittle and difficult to reason about in larger applications.

#### 5. RAG Rule Violations
*   **Magic Numbers/Strings**: The URLs are hard-coded within the function. These should be moved to named constants or a configuration file to improve maintainability.
*   **Implicit Truthiness**: While not explicitly failing here, the logic relies on `if r2.status_code == 200:`. For better robustness with the `requests` library, consider using `r2.raise_for_status()` or checking `r2.ok`.

### Summary of Required Changes
1.  **Refactor** the large function into three distinct functions (e.g., `get_post`, `get_all_posts`, `create_post`).
2.  **Rename** functions and variables to follow PEP 8 and be descriptive.
3.  **Replace** broad `except` blocks with specific `requests` exceptions.
4.  **Remove** global session dependency; pass the session as an argument to functions to improve testability.
5.  **Extract** hard-coded URLs into constants.