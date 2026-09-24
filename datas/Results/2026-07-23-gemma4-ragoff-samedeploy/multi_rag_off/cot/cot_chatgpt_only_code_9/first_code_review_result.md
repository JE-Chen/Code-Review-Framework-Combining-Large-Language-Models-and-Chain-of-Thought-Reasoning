### Code Review

**1. Readability & Consistency**
* **Nested Conditionals:** The `main()` function contains deeply nested `if/else` blocks for result counting. These should be flattened using `elif` for better readability.

**2. Naming Conventions**
* **Vague Variable Names:** In `process_all()`, the loop variables `u`, `p`, and `t` are too cryptic. Use `user`, `post`, and `todo` instead.

**3. Software Engineering Standards**
* **Code Duplication:** `get_users`, `get_posts`, and `get_todos` are nearly identical. These should be refactored into a single generic function (e.g., `fetch_and_cache(client, endpoint, cache_key)`).
* **Global State:** The use of `GLOBAL_CACHE` as a global dictionary creates hidden dependencies and makes the code harder to test and maintain. Consider moving the cache into the `APIClient` class or a dedicated cache manager.

**4. Logic & Correctness**
* **Error Handling:** `APIClient.fetch` returns a dictionary on error (e.g., `{"error": "..."}`). However, `process_all` assumes the return value is always a list (e.g., `for u in users:`). If an API call fails, the program will crash with a `TypeError` when trying to iterate over the error dictionary.
* **URL Construction:** `self.base_url + endpoint` is fragile. If `base_url` lacks a trailing slash or `endpoint` lacks a leading slash, the URL will be malformed. Use `urllib.parse.urljoin` or f-strings with explicit slash handling.

**5. Performance & Security**
* **Broad Exception Catching:** `except Exception as e` in `fetch` is too broad. It should catch specific `requests` exceptions (e.g., `RequestException`) to avoid silencing unexpected system errors.

**6. Documentation & Testing**
* **Missing Documentation:** There are no docstrings for the `APIClient` class or the processing functions, making the intended behavior and return types unclear.