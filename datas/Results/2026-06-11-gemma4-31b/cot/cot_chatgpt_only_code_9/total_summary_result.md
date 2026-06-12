### 1. Overall Conclusion
The PR **does not meet merge criteria** and is currently **blocked**. While the code is functionally operational under ideal conditions, it contains critical flaws regarding error handling and state management that pose a high risk of runtime crashes and make the codebase difficult to test or scale.

### 2. Comprehensive Evaluation
*   **Code Quality & Correctness**:
    *   **Critical Stability Risk**: The `fetch` method returns a dictionary on failure, but the calling functions (`get_users`, etc.) and the `process_all` loop assume a list is always returned. This will cause the application to crash (TypeError) when iterating over an error response.
    *   **Logic Bug**: There is a potential `KeyError` in `process_all` when accessing `p["title"]` directly after a `.get()` check.
    *   **Broad Exception Handling**: The use of `except Exception` masks potential bugs and hinders debugging.
*   **Maintainability & Design**:
    *   **High Coupling**: The code relies heavily on global mutable state (`SESSION`, `GLOBAL_CACHE`), which prevents thread safety and complicates unit testing.
    *   **Code Duplication**: `get_users`, `get_posts`, and `get_todos` are virtually identical, violating DRY principles and increasing maintenance overhead.
    *   **Architecture**: `process_all` violates the Single Responsibility Principle by handling both orchestration and business filtering logic.
*   **Consistency & Standards**:
    *   **Naming**: Use of non-descriptive variables (`u`, `p`, `t`) fails semantic clarity standards.
    *   **Formatting**: The code uses outdated string concatenation (`+`) instead of f-strings and contains an "Arrow Anti-pattern" (deeply nested `if/else`) in `main()`.
    *   **Missing Standards**: There are no type hints, docstrings, or unit tests provided.

### 3. Final Decision Recommendation
**Request Changes**

**Justification**:
The PR contains high-priority issues that must be resolved before merging:
1.  **Correctness**: Fix the data pipeline to prevent crashes when the API returns an error.
2.  **Stability**: Remove global mutable state in favor of dependency injection (encapsulate session/cache in `APIClient`).
3.  **Refactoring**: Consolidate duplicated API fetching logic into a single generic function.

### 4. Team Follow-up
*   **Refactor API Layer**: Implement a generic `get_resource` function and move `SESSION` and `GLOBAL_CACHE` into the `APIClient` class.
*   **Harden Error Handling**: Replace error dictionaries with a consistent result pattern or custom exceptions; ensure all loops validate data types before iteration.
*   **Cleanup Logic**: Flatten the nested conditionals in `main()` using an `if-elif-else` chain and rename loop variables to `user`, `post`, and `todo`.
*   **Security/Best Practice**: Transition to `urllib.parse.urljoin` for URL construction and add missing type hints.