### Code Review

**Logic & Correctness**
* **Potential Crash in `/items`**: The code calls `len(item)` and `item.upper()`. If `item` is not a string (e.g., an integer or `None` passed via `/add`), the application will throw a `TypeError` and return a 500 error.
* **Broad Exception Handling**: The `try...except Exception` in `/add` catches all errors, including system-level ones, and returns them as strings. This can leak internal server details to the client.

**Software Engineering Standards**
* **Global State**: Use of `global` variables (`DATA_STORE`, `USER_COUNT`) makes the application thread-unsafe and difficult to scale or test. Consider using a database or a proper state management class.
* **Deep Nesting**: The `/complex` route contains deeply nested `if/else` blocks (arrow code). This should be refactored using guard clauses to improve readability.
* **Hardcoded Configuration**: `CONFIG` is a global dictionary. Configuration should ideally be handled via environment variables or a dedicated config object.

**Naming Conventions**
* **Generic Naming**: `DATA_STORE` and `item` are very generic. Use more descriptive names (e.g., `USER_ITEMS_LIST`) to clarify what data is actually being stored.

**Performance & Security**
* **Input Validation**: The `/add` route does not validate the content or size of the `item` being added, which could lead to memory exhaustion (DoS) if very large strings are sent.

**Suggestions for Improvement**
* **Refactor `/complex`**: Use early returns to flatten the logic.
* **Type Checking**: Add a check in `/add` to ensure `item` is a string before appending it to the store.
* **State Management**: Move global variables into a context-aware store or database.