Here is the code review based on the provided global rules.

### 1. Readability & Consistency
- **Formatting:** The code is generally well-formatted and follows standard Python indentation.
- **String Concatenation:** The code uses `+` for string concatenation (e.g., `"Bad status: " + str(response.status_code)`). For better readability and performance, f-strings are recommended in modern Python.

### 2. Naming Conventions
- **Naming:** Variable and function names (`APIClient`, `get_users`, `process_all`) are descriptive and follow standard naming conventions.

### 3. Software Engineering Standards
- **Code Duplication:** There is significant duplication in the `get_users`, `get_posts`, and `get_todos` functions. All three perform the exact same logic: fetch data and update a global cache.
    - *Recommendation:* Refactor into a single generic function: `def fetch_and_cache(client, endpoint, cache_key):`.
- **Modularity:** The `process_all` function handles too many responsibilities (fetching data, filtering users, filtering posts, and filtering todos). These should be split into separate logic handlers.
- **Global State:** The use of `GLOBAL_CACHE` as a global dictionary makes the code harder to test and can lead to side effects in larger applications.

### 4. Logic & Correctness
- **Error Handling:** The `APIClient.fetch` method catches all exceptions (`Exception as e`) and returns them as a dictionary. This masks the difference between a network failure and a logic error, and it forces the calling functions to check for an `"error"` key in the returned data.
- **Potential Crash:** In `process_all`, the code uses `p["title"]` for posts, but `u.get("name")` for users. If a post object is missing the `"title"` key, the program will raise a `KeyError` and crash.
- **Nested Conditionals:** The `main()` function contains deeply nested `if/else` blocks for result counting, which reduces readability.

### 5. Performance & Security
- **Resource Management:** The use of `requests.Session()` is a good practice for performance as it reuses TCP connections.
- **Input Validation:** The `APIClient` blindly concatenates `base_url + endpoint`. While not a security risk with hardcoded constants, it could lead to malformed URLs if endpoints are passed dynamically without leading slashes.

### 6. Documentation & Testing
- **Documentation:** There are no docstrings or comments explaining the purpose of the classes or functions.
- **Testing:** No unit tests are provided for the API client or the processing logic.

---

### Summary of Recommendations

| Category | Issue | Priority | Suggestion |
| :--- | :--- | :--- | :--- |
| **Engineering** | Duplicated fetch/cache logic | Medium | Create a generic `fetch_and_cache` helper. |
| **Correctness** | Potential `KeyError` in posts loop | High | Use `.get("title")` consistently. |
| **Engineering** | Global state (`GLOBAL_CACHE`) | Medium | Pass a cache object or use a class-based state. |
| **Readability** | Deeply nested `if` in `main()` | Low | Use `elif` to flatten the logic. |
| **Correctness** | Generic `Exception` catching | Medium | Catch specific `requests` exceptions (e.g., `RequestException`). |