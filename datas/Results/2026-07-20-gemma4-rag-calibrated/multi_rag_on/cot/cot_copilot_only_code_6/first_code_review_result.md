### Code Review

**Logic & Correctness**
* **Potential Crash in `/items`**: The code calls `len(item)` and `item.upper()`. If `item` is not a string (e.g., an integer or `None` passed via `/add`), the application will throw a `TypeError` and crash the request.

**Software Engineering Standards & RAG Rules**
* **Shared Mutable State**: The use of `global DATA_STORE` and `USER_COUNT` introduces hidden coupling and makes the code difficult to test or scale. State should be encapsulated in a class or a database.
* **Deeply Nested Logic**: The `/complex` route contains deeply nested `if/else` blocks. This increases cognitive load and should be refactored using guard clauses (early returns).
* **Single Responsibility**: The `/items` route handles both filtering logic and response formatting. The logic for processing items based on `CONFIG` should be moved to a separate helper function.

**Naming & Readability**
* **Generic Naming**: `DATA_STORE` and `USER_COUNT` are somewhat vague. More descriptive names (e.g., `ITEM_REPOSITORY`) would better reflect their purpose.

**Performance & Security**
* **Broad Exception Handling**: The `try...except Exception` block in `/add` is too broad. It catches all errors (including syntax or system errors) and returns them to the user, which can leak internal implementation details.

**Suggestions for Improvement**
* **Refactor `/complex`**: Use guard clauses to flatten the logic.
* **Input Validation**: Validate that `item` is a string in `/add` before appending it to the store.
* **State Management**: Move global variables into a configuration object or a data access layer.