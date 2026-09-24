### Code Review

**Software Engineering Standards & RAG Rules**
*   **Shared Mutable State:** The use of `GLOBAL_STATE` as a module-level dictionary introduces hidden coupling and makes the code difficult to test and reason about. Prefer encapsulating state within a class or passing it explicitly as an argument to functions.
*   **Deeply Nested Logic:** The `process_items` function contains nested `if/else` blocks. This increases cognitive load and should be refactored using guard clauses or by splitting the logic into smaller, focused functions (e.g., `process_flagged_item` and `process_unflagged_item`).

**Naming Conventions**
*   **Vague Naming:** `flag` and `mode` are non-descriptive. Use names that reflect the actual business intent (e.g., `is_processing_enabled` or `operation_mode`).

**Logic & Correctness**
*   **Magic Numbers:** The value `77` in `GLOBAL_STATE["threshold"]` is a magic number. It should be defined as a named constant to improve maintainability.

**Readability & Consistency**
*   **Formatting:** The code is generally well-formatted and follows consistent indentation.

**Suggestions for Improvement**
*   **Refactor to Class:** Move `GLOBAL_STATE` and its associated functions into a `StateManager` or `Processor` class to eliminate global state.
*   **Simplify Conditionals:** In `process_items`, use a ternary operator or separate helper functions to flatten the nested logic.
*   **Define Constants:** Replace `77` with a constant like `DEFAULT_THRESHOLD = 77`.