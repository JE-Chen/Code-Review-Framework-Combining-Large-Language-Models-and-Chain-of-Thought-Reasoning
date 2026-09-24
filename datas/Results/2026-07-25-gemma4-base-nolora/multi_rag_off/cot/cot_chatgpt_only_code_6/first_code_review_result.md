### Code Review

**Logic & Correctness**
*   **Type Safety (GET /user):** `int(min_age)` will raise a `ValueError` (500 Internal Server Error) if the query parameter is not a valid integer. It should be wrapped in a try-except block or validated.
*   **State Management:** The use of `global LAST_RESULT` and global lists (`USERS`, `REQUEST_LOG`) is not thread-safe. In a production WSGI environment, this will lead to race conditions and inconsistent data across worker processes.

**Software Engineering Standards**
*   **Modularity:** The `user_handler` function is overloaded. It handles four different HTTP methods in one large block. This should be split into separate functions (e.g., `create_user`, `get_users`, etc.) for better maintainability.
*   **Data Persistence:** Using in-memory lists for data storage is unsuitable for anything beyond a basic prototype.

**Naming Conventions**
*   **Vague Naming:** The endpoint `/doStuff` and function `do_stuff` are non-descriptive. They should be renamed to reflect the actual business logic they perform.
*   **Variable Naming:** In `do_stuff`, variables `x` and `y` are too generic.

**Readability & Consistency**
*   **Manual JSON Construction:** In the `/stats` endpoint, the JSON response is built using string concatenation. This is error-prone and inconsistent with the rest of the app. Use `jsonify()` or `json.dumps()`.

**Performance & Security**
*   **Complexity:** The `/stats` endpoint iterates through the entire `REQUEST_LOG` three separate times. This can be optimized to a single pass.
*   **Input Validation:** The `PUT` and `DELETE` methods do not validate if `id` is provided in the request body, which could lead to unexpected behavior.

**Suggestions for Improvement**
*   **Refactor `user_handler`:** Split the logic into dedicated functions per HTTP method.
*   **Use `jsonify`:** Replace the manual string building in `/stats` with `return jsonify({"creates": create_count, ...})`.
*   **Add Validation:** Implement basic input validation for `min_age` and `user_id`.
*   **Rename `/doStuff`:** Change to a name that describes the calculation being performed.