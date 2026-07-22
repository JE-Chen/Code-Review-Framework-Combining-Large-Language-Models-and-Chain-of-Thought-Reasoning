### Code Review

**Software Engineering Standards & Logic**
* **Duplicate Code:** `get_users`, `get_posts`, and `get_comments` share identical logic. Refactor into a single generic function (e.g., `fetch_data(endpoint)`) to improve maintainability.
* **Global State:** The use of `GLOBAL_RESULTS` creates a side-effect-driven architecture. `process_data` should return a list, and `main` should handle the output.
* **Error Handling:** `response.json()` is called without checking `response.status_code` or calling `response.raise_for_status()`. This will cause a crash if the API returns a non-JSON error page.

**Naming Conventions**
* **Vague Naming:** In `process_data`, variables `u`, `p`, and `c` are too cryptic. Use `user`, `post`, and `comment`.
* **Vague Naming:** In `main`, the variable `r` should be renamed to `result`.

**Readability & Consistency**
* **Nested Logic:** The nested `if/else` block in `main` for result counts is unnecessarily deep. Use `elif` to flatten the structure.
* **String Concatenation:** Use f-strings (e.g., `f"Special User: {user.get('name')}"`) for better readability and performance.

**Performance & Security**
* **Resource Management:** The code makes three sequential network requests. While acceptable for this scale, these could be performed concurrently if the dataset grows.