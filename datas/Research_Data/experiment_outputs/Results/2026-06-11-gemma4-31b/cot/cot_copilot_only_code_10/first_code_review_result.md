## Code Review Report

### 1. Readability & Consistency
* **Formatting:** The code is generally well-indented and clean.
* **Logic Nesting:** The `main()` function contains deeply nested `if/else` blocks for result counting, which reduces readability.

### 2. Naming Conventions
* **Variable Naming:** In `process_all()`, variables `u`, `p`, and `t` are too cryptic. Use descriptive names like `user`, `post`, and `todo`.

### 3. Software Engineering Standards
* **Code Duplication:** `get_users`, `get_posts`, and `get_todos` are virtually identical. These should be refactored into a single parameterized function (e.g., `fetch_and_cache(client, endpoint)`).
* **State Management:** The use of `GLOBAL_CACHE` as a global dictionary creates tight coupling and makes the code harder to test and maintain.
* **Modularity:** `process_all` handles both data orchestration and specific business logic (filtering users/posts/todos). These filters should be moved to separate helper functions.

### 4. Logic & Correctness
* **Error Handling:** The `APIClient.fetch` method catches all exceptions and returns a dictionary. This makes it difficult for the caller to distinguish between a successful API response and an error state.
* **Potential Crash:** In `process_all()`, `p["title"]` is accessed directly after a `.get()` check. While unlikely given the previous line, using `.get()` consistently prevents `KeyError`.
* **URL Construction:** `self.base_url + endpoint` is brittle. If `base_url` doesn't end with a slash or `endpoint` starts with one unexpectedly, the URL will be malformed.

### 5. Performance & Security
* **Input Validation:** No validation is performed on the `base_url` or `endpoint`.
* **Resource Management:** The global `SESSION` is a good practice for performance (connection pooling), but it is not closed explicitly during application shutdown.

### 6. Documentation & Testing
* **Missing Documentation:** There are no docstrings for the `APIClient` class or the processing functions.
* **Testing:** No unit tests are provided for the API interactions or the filtering logic.

---

### Summary of Suggested Improvements

*   **Refactor Data Fetching:** Replace the three similar `get_...` functions with one generic function.
*   **Improve Naming:** Rename `u`, `p`, `t` to `user`, `post`, `todo`.
*   **Flatten Logic:** Use `elif` in `main()` instead of nested `if` statements.
*   **Enhance Error Handling:** Raise custom exceptions in `APIClient` instead of returning error strings in dictionaries.
*   **Safe URL Joining:** Use `urllib.parse.urljoin` for constructing URLs.