### Code Review

**Logic & Correctness**
* **Type Safety (GET /user):** `int(min_age)` will cause a 500 Internal Server Error if the query parameter is not a valid integer. Wrap in a try-except block or validate the input.
* **Data Integrity (PUT /user):** The code updates `u["age"]` without verifying if `new_age` is present in the request body or if it is a valid number.
* **ID Collision:** Using `len(USERS) + 1` for IDs will cause duplicate IDs if users are deleted and new ones are added. Use a dedicated counter or UUIDs.

**Naming Conventions**
* **Vague Naming:** The function `do_stuff` and its variables `x` and `y` are non-descriptive. Rename them to reflect the actual business logic/calculation being performed.

**Software Engineering Standards**
* **Modularity:** The `user_handler` function is overloaded. Split the logic into separate functions for `create_user`, `get_users`, `update_user`, and `delete_user` to improve maintainability.
* **State Management:** Heavy reliance on `global` variables and in-memory lists makes the application non-thread-safe and unsuitable for production.

**Performance & Security**
* **Manual JSON Construction:** In the `/stats` route, JSON is built via string concatenation. This is error-prone and bypasses Flask's `jsonify`, which handles headers and encoding correctly. Use `jsonify({"creates": create_count, ...})`.

**Readability & Consistency**
* **Consistency:** The `/reset` route returns a plain string, while all other routes return JSON. Maintain a consistent response format across the API.