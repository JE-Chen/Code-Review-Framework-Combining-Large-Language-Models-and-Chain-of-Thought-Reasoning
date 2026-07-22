### Code Review

#### 1. Readability & Consistency
- **Formatting:** The code is generally well-formatted, but the nested `if/else` blocks in `main()` are unnecessarily deep, reducing readability.

#### 2. Naming Conventions
- **Variable Names:** In `process_all()`, the loop variables `u`, `p`, and `t` are too concise. They should be renamed to `user`, `post`, and `todo` for better semantic clarity.

#### 3. Software Engineering Standards
- **Code Duplication:** The functions `get_users`, `get_posts`, and `get_todos` are nearly identical. This is a violation of the DRY (Don't Repeat Yourself) principle.
    - *Recommendation:* Create a generic `get_resource(client, resource_name)` function.
- **Modularity:** The `APIClient` is a good start, but the reliance on a global `SESSION` and `GLOBAL_CACHE` makes the code harder to test in isolation and can lead to side effects in multi-threaded environments.

#### 4. Logic & Correctness
- **Error Handling:** The `fetch` method catches all exceptions and returns a dictionary with an `"error"` key. However, the calling functions (`get_users`, etc.) and `process_all` do not check if the returned data is an error dictionary before iterating over it.
    - *Bug:* If `fetch` returns `{"error": "..."}`, the loops in `process_all` (e.g., `for u in users:`) will iterate over the keys of the dictionary instead of a list of users, leading to incorrect logic or crashes when calling `.get()` on a string.
- **Boundary Conditions:** In `process_all`, the line `results.append("Long Post: " + p["title"])` uses direct key access `p["title"]` instead of `.get()`, which will raise a `KeyError` if the title is missing, unlike the other loops in the same function.

#### 5. Performance & Security
- **Resource Management:** The use of `requests.Session()` is a good performance choice for connection pooling.
- **Input Validation:** The `base_url` and `endpoint` are concatenated using `+`. While safe here, using `urllib.parse.urljoin` is a more robust standard for constructing URLs.

#### 6. Documentation & Testing
- **Documentation:** There are no docstrings for the class or functions, making the intended behavior and return types implicit rather than explicit.
- **Testing:** No unit tests are provided for the API client or the processing logic.

---

### Summary of Changes (PR Summary)

- **Key changes:** Implemented a basic API client to fetch and process data from a JSON placeholder service.
- **Impact scope:** New `APIClient` class and data processing pipeline for users, posts, and todos.
- **Purpose of changes:** Feature addition to demonstrate data retrieval and filtering logic.
- **Risks and considerations:** 
    - Lack of error handling in the processing loop may cause crashes if the API returns an error response.
    - Global state usage (`GLOBAL_CACHE`) may cause issues if scaled.
- **Items to confirm:** 
    - Validate the behavior of `process_all` when the API returns a non-200 status code.
    - Confirm if the global cache is required for future functionality or can be removed.