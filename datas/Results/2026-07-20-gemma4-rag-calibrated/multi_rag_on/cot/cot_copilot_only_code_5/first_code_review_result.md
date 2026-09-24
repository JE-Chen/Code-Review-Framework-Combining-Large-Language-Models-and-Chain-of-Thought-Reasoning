### Code Review

*   **Shared Mutable State (Critical):** The use of `GLOBAL_STATE` as a module-level dictionary introduces hidden coupling and makes the code difficult to test or run in parallel. 
    *   *Suggestion:* Encapsulate the state within a class (e.g., `StateManager`) and pass an instance of that class to the functions.
*   **Naming Conventions:** `GLOBAL_STATE` is descriptive, but the keys within it (e.g., `flag`, `mode`) are vague.
    *   *Suggestion:* Use more semantic names (e.g., `is_processing_enabled` instead of `flag`).
*   **Logic & Correctness:** In `process_items`, the logic depends entirely on the external state of `flag` and `threshold`, making the function's behavior unpredictable without knowing the global context.
    *   *Suggestion:* Pass `data`, `flag`, and `threshold` as explicit arguments to `process_items`.
*   **Software Engineering Standards:** The code lacks modularity. The logic for processing items is tightly coupled to the global state storage.
    *   *Suggestion:* Separate the data transformation logic from the state management logic.