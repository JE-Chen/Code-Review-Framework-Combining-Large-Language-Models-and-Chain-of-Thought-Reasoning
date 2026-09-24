### Code Review

#### 1. Readability & Consistency
- **Formatting:** The code is generally well-formatted and follows standard Python indentation.
- **Consistency:** The use of `+` for string concatenation is consistent but not idiomatic for modern Python (f-strings are preferred).

#### 2. Naming Conventions
- **Descriptive Names:** Variable names like `u`, `p`, and `t` in the `process_all` loops are too brief. They should be renamed to `user`, `post`, and `todo` for better semantic clarity.

#### 3. Software Engineering Standards
- **Code Duplication:** The functions `get_users`, `get_posts`, and `get_todos` are nearly identical. This is a violation of the DRY (Don't Repeat Yourself) principle.
    - *Recommendation:* Create a generic `get_resource(client, resource_name)` function.
- **Modularity:** The `APIClient` is a good start, but the reliance on a global `SESSION` and `GLOBAL_CACHE` makes the code harder to test in isolation and not thread-safe.

#### 4. Logic & Correctness
- **Error Handling:** The `fetch` method catches all exceptions (`Exception as e`) and returns them as a dictionary. This masks the difference between a network failure and a logic error, and it forces the caller to check for an `"error"` key in the returned data.
- **Potential Crash:** In `process_all`, the line `results.append("Long Post: " + p["title"])` uses direct key access `p["title"]` instead of `.get()`. If a post object is missing the "title" key, the program will crash with a `KeyError`, whereas other parts of the code safely use `.get()`.
- **Boundary Logic:** The nested `if/else` blocks in `main()` for result counts are deeply nested and could be simplified using `elif`.

#### 5. Performance & Security
- **Global State:** `GLOBAL_CACHE` is populated but never read from. This results in unnecessary memory consumption without providing any performance benefit.
- **Input Validation:** The `base_url` and `endpoint` are concatenated directly. While not a security risk with the current hardcoded values, it is a poor pattern that could lead to malformed URLs if inputs become dynamic.

#### 6. Documentation & Testing
- **Missing Documentation:** There are no docstrings for the `APIClient` class or the processing functions.
- **Testing:** No unit tests are provided to verify the logic of `process_all` or the error handling of `APIClient`.

---

### Summary of Changes (PR Summary)

**Key Changes**
- Implemented an `APIClient` to handle HTTP requests to a JSON placeholder API.
- Added data retrieval functions for users, posts, and todos.
- Implemented a processing pipeline to filter and categorize API data.

**Impact Scope**
- New API integration logic and data processing utility.

**Purpose of Changes**
- Feature addition: Establish a baseline for fetching and processing external API data.

**Risks and Considerations**
- **Stability:** Lack of robust error handling in the processing loop (potential `KeyError`).
- **Maintainability:** High duplication in data retrieval functions.

**Items to Confirm**
- Verify if `GLOBAL_CACHE` is intended for future use or should be removed.
- Confirm the expected behavior when the API returns an error (currently returns a dict with an "error" key).