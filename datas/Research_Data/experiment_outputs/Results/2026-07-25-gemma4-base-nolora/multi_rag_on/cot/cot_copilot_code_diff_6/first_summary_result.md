## PR Summary

*   **Key changes**: Introduced a new module `bad_requests.py` that performs GET and POST requests to a placeholder API using a global session.
*   **Purpose of changes**: Initial implementation of API request functionality.
*   **Items to confirm**: The current implementation contains several architectural and coding standard violations that require refactoring before merging.

---

## Code Review

### 1. Naming Conventions
*   **Function Naming**: `functionThatDoesTooMuchAndIsHardToUnderstand` violates Python's `snake_case` convention (PEP 8) and is not descriptively named. It should be renamed to reflect its actual purpose (e.g., `fetch_and_post_sample_data`).
*   **Variable Naming**: `weirdVariableName` is non-descriptive. It should be renamed to something meaningful, such as `post_response`.

### 2. Software Engineering Standards
*   **Modularity**: The function violates the Single Responsibility Principle. It handles three different API calls (one specific GET, one list GET, and one POST) and manages its own printing. These should be split into smaller, reusable functions.
*   **Hardcoded Values**: URLs are hardcoded inside the function. These should be moved to constants or passed as arguments to improve maintainability.

### 3. Logic & Correctness
*   **Exception Handling**: 
    *   The first `try-except` block catches `Exception`, which is too broad.
    *   The second `try-except` block uses a **bare `except:`**, which is strongly discouraged as it catches `SystemExit` and `KeyboardInterrupt`, making the program difficult to terminate.
    *   Both blocks simply print the error without proper logging or recovery logic.

### 4. Performance & Security
*   **Shared Mutable State**: The use of `GLOBAL_SESSION` at the module level introduces shared mutable state. While `requests.Session()` is useful for connection pooling, managing it as a global variable makes the code harder to test and can lead to side effects in multi-threaded environments. It is better to encapsulate the session within a class or pass it as a dependency.

### 5. Readability & Consistency
*   **Consistency**: The code mixes English variable names with Chinese print statements. For professional codebases, it is recommended to stick to one language (typically English) for logs and output unless specifically required for the end-user.

### Summary of Required Changes
| Category | Issue | Recommendation |
| :--- | :--- | :--- |
| **Naming** | `camelCase` functions/variables | Change to `snake_case`. |
| **Architecture** | Monolithic function | Split into `get_post_by_id`, `get_all_posts`, and `create_post`. |
| **Error Handling** | Bare `except:` and `except Exception:` | Catch specific `requests.exceptions.RequestException`. |
| **State** | Global `requests.Session()` | Pass the session as an argument or use a Context Manager. |
| **Clean Code** | Hardcoded URLs | Move URLs to a configuration section or constants. |