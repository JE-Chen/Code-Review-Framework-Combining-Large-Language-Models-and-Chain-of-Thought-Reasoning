### Code Review

**Software Engineering Standards**
* **Global State Dependency:** The code relies heavily on a mutable global dictionary (`GLOBAL_STATE`). This makes the functions difficult to test in isolation and can lead to unpredictable behavior in larger applications. 
    * *Suggestion:* Pass state as an argument to functions or encapsulate the state and logic within a class.

**Naming Conventions**
* **Generic Naming:** Variables like `flag` and `data` are too generic and do not convey the purpose of the information they hold.
    * *Suggestion:* Rename `flag` to something descriptive (e.g., `is_processing_enabled`) and `data` to reflect its content (e.g., `item_list`).

**Logic & Correctness**
* **State Inconsistency:** `reset_state()` sets `mode` to `"reset"`, but `init_data()` does not reset the `mode` back to `"default"`. This creates an inconsistent state transition.
    * *Suggestion:* Ensure `init_data()` or a dedicated setup function handles all state keys consistently.

**Readability & Consistency**
* **Magic Numbers:** The value `77` in `GLOBAL_STATE` is a magic number without context.
    * *Suggestion:* Define this as a named constant (e.g., `DEFAULT_THRESHOLD = 77`) to improve clarity.