### Code Review

**Logic & Correctness**
* **Potential Crash in `/items`**: The code calls `len(item)` and `item.upper()`. If a non-string value is posted via `/add`, the application will throw a 500 error. Add type validation for `item`.
* **Global State Thread-Safety**: Using `global` variables (`DATA_STORE`, `USER_COUNT`) in Flask is not thread-safe and will lead to inconsistent data in a production environment (where multiple workers are used).

**Software Engineering Standards**
* **Deep Nesting (Arrow Code)**: The `/complex` route has excessive nested `if/else` blocks. This should be refactored using guard clauses to improve readability.
* **Lack of Input Validation**: The `/add` route does not verify if `item` exists in the request JSON before appending it to the list, potentially storing `None` values.

**Naming Conventions**
* **Generic Naming**: `DATA_STORE` and `USER_COUNT` are somewhat vague. Consider more descriptive names like `ITEM_REGISTRY` or `TOTAL_REQUESTS_COUNT` depending on the actual business intent.

**Performance & Security**
* **Broad Exception Handling**: `except Exception as e` in `/add` is too broad. It catches everything and returns the raw error string to the user, which can leak internal system details.

**Suggestions for Improvement**
* **Refactor `/complex`**: Use early returns to flatten the logic.
* **Input Validation**: Ensure `request.json` is present and `item` is a string before processing.
* **State Management**: Move data storage to a database or a thread-safe cache (e.g., Redis) instead of global lists.