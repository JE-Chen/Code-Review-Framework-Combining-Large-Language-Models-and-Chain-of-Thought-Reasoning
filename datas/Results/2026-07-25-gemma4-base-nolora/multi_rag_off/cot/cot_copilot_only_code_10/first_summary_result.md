Here is the code review based on the provided global rules.

### 1. Readability & Consistency
*   **Formatting:** The code generally follows PEP 8; however, the nested `if/else` blocks in the `main()` function are unnecessarily deep, reducing readability.

### 2. Naming Conventions
*   **Variable Naming:** In `process_all()`, the loop variables `u`, `p`, and `t` are too concise. They should be renamed to `user`, `post`, and `todo` to maintain semantic clarity.

### 3. Software Engineering Standards
*   **Duplicate Code:** The functions `get_users`, `get_posts`, and `get_todos` are nearly identical. This is a violation of the DRY (Don't Repeat Yourself) principle.
    *   *Recommendation:* Create a generic `fetch_and_cache(client, endpoint, cache_key)` function.
*   **Modularity:** The `APIClient` is a good start, but the reliance on a global `SESSION` and `GLOBAL_CACHE` makes the code harder to test in isolation and not thread-safe.

### 4. Logic & Correctness
*   **Error Handling:** The `fetch` method catches all exceptions (`Exception as e`) and returns them as a dictionary. This masks the difference between a network failure and a logic error.
*   **Potential Crash:** In `process_all()`, the line `results.append("Long Post: " + p["title"])` uses direct key access (`p["title"]`) instead of `.get()`. If the API returns a post without a title, the program will raise a `KeyError` and crash, whereas other parts of the code safely use `.get()`.
*   **Boundary Logic:** The `main()` function's result counting logic is functional but overly verbose.

### 5. Performance & Security
*   **Resource Management:** The use of `requests.Session()` is a positive performance choice as it reuses TCP connections.
*   **Input Validation:** The `base_url` is concatenated directly with the `endpoint` (`self.base_url + endpoint`). While safe here, if `endpoint` were ever user-supplied, this could lead to URL manipulation.

### 6. Documentation & Testing
*   **Documentation:** There are no docstrings for the class or functions. The purpose of `process_all` is not immediately clear without reading the implementation.
*   **Testing:** No unit tests are provided. The current structure (global state) makes mocking the API difficult.

---

### Summary of Suggested Refactors

| Location | Issue | Suggestion |
| :--- | :--- | :--- |
| `get_users/posts/todos` | Code Duplication | Consolidate into one parameterized function. |
| `process_all` | Potential `KeyError` | Change `p["title"]` to `p.get("title", "Unknown")`. |
| `process_all` | Poor Naming | Rename `u, p, t` $\rightarrow$ `user, post, todo`. |
| `main` | Deep Nesting | Use `if/elif/else` instead of nested `if` blocks. |
| Global Scope | State Management | Move `GLOBAL_CACHE` into a manager class or the `APIClient`. |