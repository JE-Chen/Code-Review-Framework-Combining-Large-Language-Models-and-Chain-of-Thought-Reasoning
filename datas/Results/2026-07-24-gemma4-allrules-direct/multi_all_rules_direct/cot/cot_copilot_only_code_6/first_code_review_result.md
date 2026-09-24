### Code Review

**Logic & Correctness**
* **Input Validation:** In `add_item`, `request.json.get("item")` can return `None` if the key is missing. Appending `None` to `DATA_STORE` will cause the `get_items` route to crash when calling `len(item)` or `item.upper()`.

**Software Engineering Standards & RAG Rules**
* **Shared Mutable State:** The use of global variables (`DATA_STORE`, `USER_COUNT`) introduces hidden coupling and makes the application non-thread-safe. Use a database or a proper state management object.
* **Broad Exception Handling:** `add_item` uses `except Exception as e:`, which hides specific errors (e.g., `TypeError` or `BadRequest`) and makes debugging difficult.
* **Deeply Nested Logic:** `complex_route` contains deeply nested `if/else` blocks. This increases cognitive load and should be refactored using guard clauses or a mapping strategy.
* **Single Responsibility:** `get_items` handles both data retrieval and business logic (filtering/transforming based on `CONFIG`). This logic should be moved to a separate helper function.

**Performance & Security**
* **Inefficient Loop Logic:** In `get_items`, the check `if CONFIG["mode"] == "test"` is performed inside the loop for every item. Move this check outside the loop to avoid redundant evaluations.
* **External Input Trust:** `complex_route` processes `param` directly. While not critical here, ensure all external inputs are sanitized before use in business logic.

**Naming & Readability**
* **Magic Strings:** The strings `"test"`, `"reset"`, and `"hello"` are hard-coded. Use named constants to improve maintainability.
* **Variable Naming:** `i` in `get_items` is acceptable for an index, but `param` in `complex_route` is vague; a more descriptive name (e.g., `input_value`) would be better.

**Suggestions for Improvement**
* Replace global variables with a data repository class.
* Refactor `complex_route` to use early returns to flatten the logic.
* Add explicit validation to ensure `item` is a string before appending it to the store.
* Catch specific exceptions (e.g., `TypeError`, `KeyError`) instead of the base `Exception` class.