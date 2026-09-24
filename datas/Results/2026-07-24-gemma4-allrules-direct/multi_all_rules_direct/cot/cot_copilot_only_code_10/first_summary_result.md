### PR Summary

*   **Key changes**: Implemented an `APIClient` to fetch data from a JSON placeholder API and a processing pipeline to filter users, posts, and todos.
*   **Impact scope**: New API integration and data processing logic.
*   **Purpose of changes**: Establish a basic framework for fetching and filtering remote resources.
*   **Items to confirm**: Review the error handling strategy and the use of global state for caching.

---

### Code Review

#### 1. Logic & Correctness
*   **Inconsistent Return Types**: The `APIClient.fetch` method returns a data object (list/dict) on success but a dictionary with an `"error"` key on failure. This forces every caller to check for the existence of an `"error"` key before processing data, which is not done in `get_users`, `get_posts`, or `get_todos`. This will lead to a `TypeError` (e.g., trying to iterate over a dictionary in `process_all`) if the API call fails.

#### 2. Software Engineering Standards & RAG Rules
*   **Shared Mutable State**: The use of `GLOBAL_CACHE = {}` is a violation of the RAG rule regarding shared mutable state. It introduces hidden coupling and makes the code harder to test and reason about. State should be encapsulated within a class or passed explicitly.
*   **Broad Exception Handling**: `APIClient.fetch` uses `except Exception as e:`. This is a broad catch that can hide unexpected bugs (like `KeyboardInterrupt` or `MemoryError`). It should catch specific `requests` exceptions (e.g., `requests.RequestException`).
*   **Single Responsibility Principle**: `process_all` is doing too much: it instantiates the client, orchestrates three different API calls, and performs three different types of business logic filtering. These should be split into smaller, focused functions.

#### 3. Readability & Consistency
*   **Deeply Nested Conditionals**: The `main` function contains deeply nested `if/else` blocks to categorize the result count. This increases cognitive load.
    *   *Recommendation*: Use guard clauses or a more linear structure to simplify the flow.
*   **Naming**: Variable names like `u`, `p`, and `t` in `process_all` are too short. Use descriptive names like `user`, `post`, and `todo`.

#### 4. Performance & Security
*   **String Concatenation**: The code uses `+` for string concatenation in several places (e.g., `url = self.base_url + endpoint`). While acceptable for small strings, f-strings are preferred for readability and performance in Python.
*   **Input Validation**: While the API is internal/mocked here, the code lacks validation for the `base_url` or the structure of the returned JSON before accessing keys.

#### 5. Documentation & Testing
*   **Missing Tests**: There are no unit tests provided. The tight coupling to `SESSION` and `GLOBAL_CACHE` makes the current implementation difficult to test without making actual network calls.

### Summary of Scores & Recommendations
| Category | Status | Note |
| :--- | :--- | :--- |
| **Readability** | ⚠️ Warning | Nested logic in `main` and short variable names. |
| **Engineering** | ❌ Critical | Global mutable state and broad exception handling. |
| **Correctness** | ❌ Critical | Inconsistent return types will cause crashes on API error. |
| **Security** | ✅ Pass | No critical vulnerabilities found for this scope. |