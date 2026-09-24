### Code Review

*   **Software Engineering Standards**: The code relies heavily on a mutable global dictionary (`GLOBAL_STATE`). This makes the functions difficult to test in isolation and can lead to unpredictable side effects. Consider encapsulating the state within a class or passing the state as an argument to the functions.
*   **Naming Conventions**: The variable name `flag` is too generic. It should be renamed to reflect its actual purpose (e.g., `is_processing_mode` or `use_multiplier_logic`) to improve semantic clarity.
*   **Logic & Correctness**: In `reset_state()`, the `threshold` key is not reset, while all other state variables are. If the intention is a full reset, `threshold` should be handled or the state should be re-initialized from a default template.
*   **Readability**: The nested `if/else` blocks in `process_items()` are slightly verbose. These could be simplified using ternary operators or a helper function to improve readability.