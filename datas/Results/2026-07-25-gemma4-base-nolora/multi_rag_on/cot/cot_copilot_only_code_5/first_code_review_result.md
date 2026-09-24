### Code Review

*   **Shared Mutable State (Critical):** The use of `GLOBAL_STATE` as a module-level dictionary introduces hidden coupling and makes the code difficult to test or run in parallel. 
    *   *Suggestion:* Encapsulate the state within a class (e.g., `StateManager`) and pass an instance of that class to the functions.
*   **Naming Conventions:** The variable `flag` is too vague. It does not describe what the boolean actually controls (e.g., whether to use "multiplier mode" vs "threshold mode").
    *   *Suggestion:* Rename `flag` to something descriptive, such as `use_multiplier_mode`.
*   **Logic & Maintainability:** The `process_items` function relies heavily on external state, making it a "side-effect" function that is hard to unit test in isolation.
    *   *Suggestion:* Pass `data`, `flag`, and `threshold` as explicit arguments to `process_items`.
*   **Software Engineering Standards:** The `reset_state` function manually resets keys. If new keys are added to `GLOBAL_STATE` in the future, this function will likely be forgotten, leading to partial resets.
    *   *Suggestion:* Define a constant `DEFAULT_STATE` and assign a copy of it during reset.