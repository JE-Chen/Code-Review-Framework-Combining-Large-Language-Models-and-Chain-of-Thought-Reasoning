### Code Review

**Logic & Correctness**
* **Potential Crash in `process_all`**: The `fetch` method returns a dictionary `{"error": ...}` on failure, but `process_all` iterates over the return values (e.g., `for u in users:`). Iterating over a dictionary will yield keys instead of records, likely causing `u.get()` to raise an `AttributeError`.

**Software Engineering Standards**
* **Code Duplication**: `get_users`, `get_posts`, and `get_todos` are nearly identical. These should be refactored into a single generic function (e.g., `get_resource(client, resource_name)`).
* **Global State**: The use of `GLOBAL_CACHE` is problematic for maintainability and testing. Consider moving the cache into the `APIClient` class or a dedicated cache manager.

**Naming Conventions**
* **Vague Variable Names**: In `process_all`, variables `u`, `p`, and `t` are too cryptic. Use `user`, `post`, and `todo` for better clarity.

**Readability & Consistency**
* **Nested Conditionals**: The `main` function contains deeply nested `if/else` blocks for result counting. This should be flattened using `elif` for better readability.
* **String Concatenation**: Use f-strings (e.g., `f"Bad status: {response.status_code}"`) instead of `+` concatenation for better performance and readability.

**Performance & Security**
* **Broad Exception Handling**: `except Exception as e` in `fetch` is too broad. It should catch specific `requests` exceptions (e.g., `RequestException`) to avoid silencing unexpected system errors.