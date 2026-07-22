### Code Review

**Logic & Correctness**
* **Potential Crash in `/items`**: The code calls `len(item)` and `item.upper()`. If `item` is not a string (e.g., an integer or `None` passed via `/add`), the application will throw a `TypeError` and return a 500 error.
* **Broad Exception Handling**: The `try...except Exception` in `/add` is too generic. It catches all errors (including syntax or system errors) and returns them as strings, which can leak internal implementation details.

**Software Engineering Standards**
* **Global State**: The use of `global` variables (`DATA_STORE`, `USER_COUNT`) makes the application thread-unsafe and difficult to test. Consider using a database or a dedicated state management class.
* **Deep Nesting**: The `/complex` route contains deeply nested `if/else` blocks (arrow code). This should be refactored using guard clauses to improve readability.
* **Hardcoded Configuration**: `CONFIG` is defined as a global dictionary. These should ideally be handled via environment variables or a configuration file.

**Naming Conventions**
* **Generic Naming**: `param` in `/complex` and `item` in `/add_item` are generic. While acceptable for a small demo, more descriptive names (e.g., `input_value`) are preferred.

**Performance & Security**
* **Input Validation**: There is no validation on the size or type of data being appended to `DATA_STORE`. A malicious user could send extremely large strings to exhaust server memory.

**Suggestions for Improvement**
* **Refactor `/complex`**: Use early returns to flatten the logic.
* **Type Checking**: Add `if isinstance(item, str):` before calling string methods in `/items`.
* **State Management**: Move global variables into a context-aware store or database.