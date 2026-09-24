### Code Review

**Logic & Correctness**
* **Potential Crash in `process_all`**: The `fetch` method returns a dictionary `{"error": ...}` on failure, but `process_all` iterates over the return values (e.g., `for u in users:`). If an API call fails, the code will iterate over the keys of the error dictionary instead of a list of records, leading to incorrect logic or crashes.

**Software Engineering Standards**
* **Code Duplication**: `get_users`, `get_posts`, and `get_todos` are nearly identical. These should be refactored into a single generic function (e.g., `get_resource(client, resource_name)`).
* **Global State**: The use of `GLOBAL_CACHE` is problematic for maintainability and testing. Consider moving the cache into the `APIClient` class or a dedicated cache manager.

**Naming Conventions**
* **Vague Variable Names**: In `process_all`, variables `u`, `p`, and `t` are too cryptic. Use `user`, `post`, and `todo` for better readability.

**Readability & Consistency**
* **Deep Nesting**: The `main` function contains deeply nested `if/else` blocks. This can be flattened using `elif` for better clarity.
* **String Concatenation**: Use f-strings (e.g., `f"Bad status: {response.status_code}"`) instead of `+` for better readability and performance.

**Performance & Security**
* **URL Construction**: `self.base_url + endpoint` is fragile. Use `urllib.parse.urljoin` or a similar method to ensure slashes are handled correctly.