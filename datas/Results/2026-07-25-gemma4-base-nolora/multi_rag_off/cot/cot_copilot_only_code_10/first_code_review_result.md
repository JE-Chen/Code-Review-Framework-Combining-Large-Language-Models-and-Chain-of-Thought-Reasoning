### Code Review

**Logic & Correctness**
* **Error Handling Crash:** In `process_all()`, the code iterates over `users`, `posts`, and `todos`. However, `APIClient.fetch` returns a dictionary `{"error": "..."}` on failure. Iterating over a dictionary in a `for` loop will iterate over its keys, causing `u.get("id")` to raise an `AttributeError` because `u` will be a string (the key "error").

**Software Engineering Standards**
* **Code Duplication:** `get_users`, `get_posts`, and `get_todos` are identical in logic. These should be refactored into a single generic function (e.g., `fetch_and_cache(client, endpoint, cache_key)`).
* **Global State:** The use of `GLOBAL_CACHE` is problematic for maintainability and testability. Consider moving the cache into the `APIClient` class or a dedicated Cache manager.
* **Hardcoded Logic:** The filtering logic in `process_all` (e.g., `id == 1`, `len > 15`) is tightly coupled. These should be extracted into separate filter functions.

**Naming Conventions**
* **Vague Variable Names:** In `process_all()`, the loop variables `u`, `p`, and `t` are too cryptic. Use `user`, `post`, and `todo` for clarity.

**Readability & Consistency**
* **Nested Conditionals:** The `main()` function contains deeply nested `if/else` blocks for result counting. This should be flattened using `elif` for better readability.
* **String Concatenation:** The code uses `+` for string building (e.g., `"Bad status: " + str(...)`). Use f-strings for better performance and readability.

**Performance & Security**
* **URL Construction:** `self.base_url + endpoint` is fragile. If `base_url` lacks a trailing slash or `endpoint` lacks a leading one, the URL will be malformed. Use `urllib.parse.urljoin` or a similar utility.