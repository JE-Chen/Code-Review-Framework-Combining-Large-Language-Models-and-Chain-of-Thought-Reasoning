### Code Review

**Software Engineering Standards & Modularity**
* **Duplicate Logic:** The functions `get_users`, `get_posts`, and `get_todos` are nearly identical. These should be refactored into a single generic function (e.g., `fetch_and_cache(client, endpoint, cache_key)`) to reduce redundancy.
* **Global State:** The use of `GLOBAL_CACHE` as a global dictionary creates tight coupling and makes the code harder to test and maintain. Consider moving the cache into the `APIClient` class or a dedicated Cache manager.

**Logic & Correctness**
* **Error Handling Leakage:** The `fetch` method returns a dictionary `{"error": ...}` on failure. However, `process_all` assumes the return value is always a list (e.g., `for u in users:`). If an API call fails, the code will raise a `TypeError` when attempting to iterate over the error dictionary.
* **Potential Crash:** In the `posts` loop, `p["title"]` is accessed directly after checking `p.get("title", "")`. If the key `"title"` is missing, the `get` check passes (empty string), but the subsequent direct access will raise a `KeyError`. Use `.get()` consistently.

**Readability & Naming**
* **Vague Naming:** In `process_all`, variables `u`, `p`, and `t` are too cryptic. Use `user`, `post`, and `todo` for better semantic clarity.
* **Nested Conditionals:** The `main()` function contains deeply nested `if/else` blocks for result counting. This should be flattened using `elif` for better readability.

**Performance & Security**
* **URL Construction:** `url = self.base_url + endpoint` is fragile. If `base_url` lacks a trailing slash or `endpoint` lacks a leading slash, the URL will be malformed. Use `urllib.parse.urljoin` or a similar utility.

**Suggestions for Improvement**
* **Refactor:** Create a helper method for the repetitive fetch/cache pattern.
* **Validation:** Add a check in `process_all` to ensure the data returned from the client is a list before iterating.
* **Formatting:** Flatten the logic in `main()` using an `if/elif/else` chain.