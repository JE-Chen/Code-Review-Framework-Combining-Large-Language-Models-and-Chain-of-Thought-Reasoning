### Code Review

**Logic & Correctness**
* **Error Handling Leakage:** `get_users`, `get_posts`, and `get_todos` do not check if `client.fetch` returned an error dictionary. This will cause `process_all` to crash (e.g., `TypeError: string indices must be integers`) when iterating over the error response.

**Software Engineering Standards**
* **Code Duplication:** `get_users`, `get_posts`, and `get_todos` are nearly identical. These should be refactored into a single generic function (e.g., `fetch_and_cache(client, endpoint, cache_key)`).
* **Global State:** The use of `GLOBAL_CACHE` is unnecessary and creates side effects that make the code harder to test and maintain.

**Naming Conventions**
* **Vague Variable Names:** In `process_all`, variables `u`, `p`, and `t` are too cryptic. Use `user`, `post`, and `todo` for clarity.

**Readability & Consistency**
* **Nested Conditionals:** The `main()` function contains deeply nested `if/else` blocks for result counting. This should be flattened using `elif` for better readability.
* **String Concatenation:** Use f-strings (e.g., `f"Bad status: {response.status_code}"`) instead of `+` operators for better performance and readability.

**Performance & Security**
* **URL Construction:** `self.base_url + endpoint` is fragile. Use `urllib.parse.urljoin` or a similar method to ensure slashes are handled correctly.