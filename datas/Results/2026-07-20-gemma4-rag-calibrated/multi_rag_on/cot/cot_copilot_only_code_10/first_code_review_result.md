### Code Review

**Logic & Correctness**
* **Potential Crash in `process_all`**: The `fetch` method returns a dictionary `{"error": "..."}` on failure, but `process_all` iterates over the return values (e.g., `for u in users:`). Iterating over a dictionary yields keys, not records, and will cause logic errors or crashes when calling `.get()` on a string key.

**Software Engineering Standards**
* **Code Duplication**: `get_users`, `get_posts`, and `get_todos` are identical in logic. These should be refactored into a single parameterized function (e.g., `fetch_and_cache(client, endpoint, cache_key)`).
* **Global State**: The use of `GLOBAL_CACHE` creates hidden dependencies and makes the code harder to test and maintain. Consider moving the cache into the `APIClient` or a dedicated Cache manager.

**Naming Conventions**
* **Vague Variable Names**: In `process_all`, variables `u`, `p`, and `t` are too cryptic. Use `user`, `post`, and `todo` for clarity.

**Readability & Consistency**
* **Deep Nesting**: The `main` function contains deeply nested `if/else` blocks. This should be flattened using `elif` for better readability.
* **String Concatenation**: Use f-strings (e.g., `f"Bad status: {response.status_code}"`) instead of `+` for better performance and readability.

**Performance & Security**
* **Broad Exception Handling**: `except Exception as e` in `APIClient.fetch` is too broad. It should catch specific `requests` exceptions (e.g., `RequestException`) to avoid silencing unexpected system errors.