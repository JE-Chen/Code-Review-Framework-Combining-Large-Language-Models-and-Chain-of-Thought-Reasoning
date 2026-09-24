### Pull Request Summary

*   **Key changes**: Implemented an `APIClient` to fetch data from a REST API and a processing pipeline to filter users, posts, and todos.
*   **Impact scope**: New API integration and data processing logic.
*   **Purpose of changes**: Establish a basic framework for retrieving and filtering external data.
*   **Items to confirm**: Review the error handling strategy in `APIClient.fetch` and the use of the global cache.

---

### Code Review

#### 1. Readability & Consistency
*   **Formatting**: The code is generally well-formatted, but the nested `if/else` blocks in `main()` are unnecessarily deep. Using `elif` would improve readability.

#### 2. Naming Conventions
*   **Variable Names**: In `process_all()`, variables `u`, `p`, and `t` are too concise. Use `user`, `post`, and `todo` to maintain semantic clarity.

#### 3. Software Engineering Standards
*   **Duplicate Code**: The functions `get_users`, `get_posts`, and `get_todos` are nearly identical. This is a violation of the DRY (Don't Repeat Yourself) principle.
    *   *Recommendation*: Create a generic `get_resource(client, resource_name)` function.
*   **Modularity**: The `APIClient` is a good start, but the dependency on a global `SESSION` and `GLOBAL_CACHE` makes the code harder to test in isolation and not thread-safe.

#### 4. Logic & Correctness
*   **Potential Crash**: In `process_all()`, the line `results.append("Long Post: " + p["title"])` uses direct key access (`p["title"]`) whereas other parts of the code use `.get()`. If the API returns a post without a title, this will raise a `KeyError`.
*   **Error Handling**: `APIClient.fetch` catches all exceptions and returns them as a dictionary `{"error": ...}`. However, the calling functions (`get_users`, etc.) do not check if the returned data is an error dictionary before passing it to `process_all()`. This will cause `process_all()` to crash when it tries to iterate over a dictionary (e.g., `for u in users:` where `users` is `{"error": "..."}`).

#### 5. Performance & Security
*   **Resource Management**: The use of a global `requests.Session()` is a good performance practice for connection pooling.
*   **Input Validation**: The `base_url` is concatenated directly with the endpoint. While safe here, using `urllib.parse.urljoin` is a more robust standard for URL construction.

#### 6. Documentation & Testing
*   **Missing Tests**: No unit tests are provided for the `APIClient` or the filtering logic in `process_all`.
*   **Documentation**: The code lacks docstrings explaining the purpose of the classes and functions.

### Summary of Recommendations
1.  **Refactor** `get_users/posts/todos` into a single parameterized function.
2.  **Fix** the bug in `process_all` where it assumes the API response is always a list.
3.  **Standardize** dictionary access to use `.get()` consistently to avoid `KeyError`.
4.  **Flatten** the conditional logic in `main()` using `elif`.
5.  **Inject** the session into the `APIClient` rather than relying on a global variable to improve testability.