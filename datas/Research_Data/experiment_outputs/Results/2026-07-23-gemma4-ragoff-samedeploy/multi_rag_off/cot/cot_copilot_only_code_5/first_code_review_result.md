### Code Review

**Naming Conventions**
* `GLOBAL_STATE`: While descriptive, using a global dictionary for state management is generally discouraged in favor of classes or configuration objects to improve maintainability and testability.
* `flag`: This name is too vague. It should be renamed to reflect its actual purpose (e.g., `use_multiplier_mode` or `is_processing_enabled`).

**Software Engineering Standards**
* **Global State Dependency**: The functions `init_data`, `increment_counter`, `toggle_flag`, `process_items`, and `reset_state` are tightly coupled to the `GLOBAL_STATE` object. This makes unit testing difficult as tests cannot be run in isolation without resetting global state.
* **Suggestion**: Pass the state as an argument to these functions or encapsulate the logic within a class.

**Logic & Correctness**
* **`reset_state` inconsistency**: The `reset_state` function sets `GLOBAL_STATE["mode"] = "reset"`, but the initial state is `"default"`. It is unclear if "reset" is a valid operational mode or just a marker.

**Readability & Consistency**
* The code is well-formatted and follows consistent indentation.

**Summary of Suggestions**
* Rename `flag` to something more descriptive.
* Refactor the global dictionary into a class to improve modularity and testability.