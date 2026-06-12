## Code Review Report

### 1. Readability & Consistency
* **Formatting:** The code is generally well-indented, but `main()` contains deeply nested `if/else` blocks that reduce readability.
* **Consistency:** String concatenation is used (`+`) instead of f-strings, which is less idiomatic in modern Python.

### 2. Naming Conventions
* **Variable Names:** In `process_all()`, loop variables `u`, `p`, and `t` are too cryptic. Use `user`, `post`, and `todo` for better clarity.
* **Global Constants:** `SESSION` and `GLOBAL_CACHE` follow naming conventions, but their usage as global state is problematic.

### 3. Software Engineering Standards
* **Code Duplication:** `get_users`, `get_posts`, and `get_todos` are nearly identical. These should be refactored into a single generic function (e.g., `get_resource(client, endpoint)`).
* **Modularity:** The `APIClient` is too basic. The `SESSION` object is defined globally rather than being encapsulated within the `APIClient` class.
* **Tight Coupling:** The `get_*` functions rely on a global `GLOBAL_CACHE` variable, making them difficult to test in isolation and prone to side effects.

### 4. Logic & Correctness
* **Error Handling:** The `fetch` method returns a dictionary `{"error": ...}` on failure. However, the calling functions (`get_users`, etc.) do not check if the returned data is an error dictionary before treating it as a list, which will lead to crashes in `process_all` (e.g., iterating over a dictionary).
* **Boundary Conditions:** `p["title"]` in the posts loop is accessed via bracket notation after a `.get()` check; if `title` is missing, it will raise a `KeyError`.

### 5. Performance & Security
* **Resource Management:** While `requests.Session()` is used (which is good), the global state management of the cache is not thread-safe.
* **Input Validation:** `self.base_url + endpoint` is used for URL construction. Using `urllib.parse.urljoin` is safer to avoid issues with trailing/leading slashes.

### 6. Documentation & Testing
* **Missing Docs:** There are no docstrings for classes or functions to explain their purpose or expected return types.
* **Testing:** No unit tests are provided to verify the `APIClient` or the processing logic.

---

### Summary of Improvement Suggestions

| Location | Suggestion | Reason |
| :--- | :--- | :--- |
| `APIClient` | Move `SESSION` inside the class as an instance attribute. | Improves encapsulation and modularity. |
| `get_*` functions | Consolidate into one function: `fetch_and_cache(client, endpoint, cache_key)`. | Removes redundant code. |
| `process_all` | Replace `u`, `p`, `t` with `user`, `post`, `todo`. | Improves semantic clarity. |
| `fetch` method | Raise a custom exception or return a consistent Result object. | Prevents the application from crashing when iterating over error responses. |
| `main` | Flatten nested `if/else` using `elif` or a mapping. | Improves readability. |
| Throughout | Use f-strings: `f"Results: {r}"` instead of `"Results: " + r`. | Follows Python best practices. |