### Code Review

#### 1. Readability & Consistency
- **Formatting**: The code is generally clean and follows standard indentation.
- **String Concatenation**: The code uses `+` for string concatenation (e.g., `"Bad status: " + str(response.status_code)`). It is recommended to use f-strings for better readability and performance.

#### 2. Naming Conventions
- **Variable Names**: In `process_all`, the loop variables `u`, `p`, and `t` are too concise. They should be renamed to `user`, `post`, and `todo` to maintain semantic clarity.

#### 3. Software Engineering Standards
- **Code Duplication**: The functions `get_users`, `get_posts`, and `get_todos` are nearly identical. This is a violation of the DRY (Don't Repeat Yourself) principle.
    - *Recommendation*: Create a generic `fetch_and_cache(client, endpoint, cache_key)` function.
- **Modularity**: The `APIClient` is a good start, but the caching logic is handled by global functions rather than the client or a dedicated cache manager.

#### 4. Logic & Correctness
- **Error Handling**: The `fetch` method returns a dictionary `{"error": ...}` on failure. However, the calling functions (`get_users`, etc.) and `process_all` do not check if the returned data is an error dictionary before iterating over it.
    - *Bug*: If `client.fetch` returns an error dictionary, the `for u in users:` loop will iterate over the keys of the error dictionary (e.g., "error") instead of a list of users, likely leading to unexpected behavior or crashes when calling `.get("id")`.
- **Boundary Conditions**: In `process_all`, `p["title"]` is accessed directly without `.get()`, whereas other fields use `.get()`. If a post is missing a title, this will raise a `KeyError`.

#### 5. Performance & Security
- **Global State**: `GLOBAL_CACHE` is a global variable. In a multi-threaded environment, this could lead to race conditions.
- **Resource Management**: The use of `requests.Session()` is a good performance practice as it reuses TCP connections.

#### 6. Documentation & Testing
- **Documentation**: There are no docstrings for the class or functions.
- **Testing**: No unit tests are provided to verify the logic of `process_all` or the error handling of `APIClient`.

---

### Summary of Recommendations

| Category | Issue | Severity | Suggestion |
| :--- | :--- | :--- | :--- |
| **Logic** | Error response handled as iterable | High | Check for `"error"` key before iterating in `process_all`. |
| **Engineering** | Repetitive fetch functions | Medium | Refactor `get_users/posts/todos` into a single parameterized function. |
| **Logic** | Potential `KeyError` on `p["title"]` | Medium | Use `.get("title", "")` consistently. |
| **Naming** | Non-descriptive loop variables | Low | Rename `u, p, t` to `user, post, todo`. |
| **Readability** | String concatenation | Low | Use f-strings. |