### Code Review

**Software Engineering Standards**
* **Global State Dependency:** The code relies heavily on a mutable global dictionary (`GLOBAL_STATE`). This makes the functions difficult to test in isolation and can lead to unpredictable behavior in larger applications. 
    * *Suggestion:* Pass the state as an argument to functions or encapsulate the state and logic within a class.

**Naming Conventions**
* **Generic Naming:** Variables like `flag` and `data` are too vague. They describe the data type or a generic state rather than the purpose of the value.
    * *Suggestion:* Rename `flag` to something descriptive (e.g., `is_multiplier_mode`) and `data` to reflect what the items actually represent.

**Logic & Correctness**
* **State Inconsistency:** `reset_state()` sets `mode` to `"reset"`, but `init_data()` does not set a mode, and `process_items()` never checks the `mode` key. The `mode` variable is currently dead code.
    * *Suggestion:* Either utilize the `mode` variable in the logic or remove it from the state.

**Readability & Consistency**
* **Magic Numbers:** The value `77` in `threshold` is a magic number without context.
    * *Suggestion:* Define this as a named constant at the top of the file to explain its significance.