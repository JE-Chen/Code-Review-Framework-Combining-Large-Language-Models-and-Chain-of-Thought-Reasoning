- **Global Variables & State Management**:  
  `DATA_STORE`, `USER_COUNT`, and `CONFIG` are global variables, violating modularity and testability. Replace with encapsulated state (e.g., a `DataStore` class) to avoid side effects and improve maintainability.

- **Input Validation Gaps**:  
  `add_item` appends `None` if `"item"` is missing (no validation). Return 400 error for missing/invalid items instead of silent failure.

- **Overly Nested Logic**:  
  `/complex` route has deep conditionals with repeated `int(param)` conversions. Simplify with early returns and single conversions for readability and performance.

- **Unclear Configuration State**:  
  `CONFIG["mode"] = "reset"` in `/reset` is ambiguous and unused. Replace with explicit reset logic; avoid reusing `mode` for non-mode states.

- **Hardcoded Magic Values**:  
  `CONFIG["threshold"] = 123` lacks context. Use descriptive constants (e.g., `MAX_ITEM_LENGTH = 123`) or document purpose.

- **Missing Documentation**:  
  Functions lack docstrings explaining purpose, inputs, and outputs. Add concise summaries for maintainability.

- **Inconsistent Error Handling**:  
  `add_item` catches *all* exceptions (e.g., `KeyError` for missing JSON). Log errors and return specific HTTP status codes (e.g., `400 Bad Request`).

- **Redundant Code**:  
  `get_items` duplicates logic for `CONFIG["mode"]`. Extract mode-specific processing into helper functions to avoid repetition.