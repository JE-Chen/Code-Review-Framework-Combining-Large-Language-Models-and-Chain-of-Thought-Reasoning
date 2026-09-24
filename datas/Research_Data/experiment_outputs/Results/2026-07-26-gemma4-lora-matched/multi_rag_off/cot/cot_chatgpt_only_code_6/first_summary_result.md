Here is the code review based on the provided global rules.

### 1. Readability & Consistency
- **Inconsistent Response Formats**: The `/reset` endpoint returns a plain string, while all other endpoints return JSON. For API consistency, `/reset` should return a JSON object (e.g., `{"status": "reset done"}`).
- **Manual JSON Construction**: In the `/stats` endpoint, JSON is constructed via string concatenation. This is error-prone and deviates from the use of `jsonify` seen elsewhere in the code.

### 2. Naming Conventions
- **Function Naming**: The function `do_stuff` is non-descriptive. It should be renamed to reflect the actual mathematical operation it performs (e.g., `calculate_weighted_average`).

### 3. Software Engineering Standards
- **Lack of Modularity**: The `user_handler` function is overloaded, handling four different HTTP methods in one large block. This should be split into separate functions (e.g., `create_user`, `get_users`, `update_user`, `delete_user`) to improve maintainability and testability.
- **Global State**: The use of `global LAST_RESULT` across multiple endpoints creates tight coupling and makes the code difficult to test in isolation.

### 4. Logic & Correctness
- **Type Safety (Casting)**: In the `GET /user` handler, `int(min_age)` is called without a `try-except` block. If a user provides a non-numeric string (e.g., `?min_age=abc`), the server will crash with a `500 Internal Server Error`.
- **Data Integrity**: In the `PUT` handler, `u["age"] = new_age` is performed without validating that `new_age` is actually provided in the request body or that it is a valid number. This could result in `age` being set to `None`.

### 5. Performance & Security
- **Concurrency Issues**: The code uses global lists (`USERS`, `REQUEST_LOG`) without any locking mechanisms. In a production environment (where Flask typically runs with multiple threads/workers), this will lead to **race conditions** and data corruption.
- **Complexity**: The `/stats` endpoint iterates through the entire `REQUEST_LOG` three separate times. While negligible for small logs, this is $O(3N)$ and should be reduced to a single pass.
- **Input Validation**: There is no validation on the `x` and `y` inputs in `/doStuff`. If a non-numeric type is passed, the application will throw an unhandled exception.

### 6. Documentation & Testing
- **Missing Documentation**: There are no docstrings explaining the API contracts or the purpose of the endpoints.
- **Missing Tests**: No unit tests are provided to verify the logic of the user management or the calculation endpoint.

---

### Summary of Recommendations
| Priority | Issue | Recommendation |
| :--- | :--- | :--- |
| **High** | Thread Safety | Replace global lists with a database or implement thread-safe primitives. |
| **High** | Input Validation | Wrap `int()` casts in try-except blocks and validate `PUT` payloads. |
| **Medium** | Refactoring | Split `user_handler` into method-specific functions. |
| **Medium** | Consistency | Use `jsonify` in `/stats` and `/reset` instead of manual strings. |
| **Low** | Naming | Rename `do_stuff` to something descriptive. |