## Code Review Report

### 1. Readability & Consistency
- **Formatting**: General formatting is clean and follows PEP 8 standards.
- **Consistency**: The use of mixed-case strings for labels and window titles is inconsistent (some are casual, some are descriptive).

### 2. Naming Conventions
- **`GLOBAL_THING`**: Poorly named. It is too vague and does not describe the purpose of the data it holds. Suggest renaming to `app_state` or `session_data`.
- **`do_periodic_stuff`**: Vague function name. Suggest renaming to `update_ui_randomly` or `refresh_dynamic_elements`.
- **`compute_title`**: The function does more than "compute" (it modifies state). Suggest `update_and_get_title`.

### 3. Software Engineering Standards
- **Global State**: The use of a global dictionary (`GLOBAL_THING`) for state management makes the code harder to test and scale. This state should be encapsulated within the `MyWindow` class or a dedicated State manager class.
- **Modularity**: Logic for updating the UI is tightly coupled with the state modification logic.

### 4. Logic & Correctness
- **UI Blocking**: `time.sleep(0.1)` inside `handle_click` is called on the main GUI thread. While 100ms is short, using `sleep` in a GUI event loop can cause the interface to freeze or stutter.
- **State Side-Effects**: `compute_title()` changes the global state as a side effect of returning a string. This makes the behavior unpredictable when calling the function for simple read operations.

### 5. Performance & Security
- **Resource Management**: No critical security vulnerabilities found.
- **Efficiency**: The `QTimer` interval (777ms) is arbitrary but acceptable for this scale.

### 6. Documentation & Testing
- **Documentation**: There are no docstrings or comments explaining the purpose of the logic (especially the modulo checks).
- **Testing**: No unit tests are provided for the state transition logic or the text generation logic.

---

### Summary of Suggestions
| Issue | Priority | Suggestion |
| :--- | :--- | :--- |
| **Global State** | High | Move `GLOBAL_THING` into `MyWindow` as `self.state`. |
| **Naming** | Medium | Rename `GLOBAL_THING` $\rightarrow$ `AppState` and `do_periodic_stuff` $\rightarrow$ `update_periodic_ui`. |
| **UI Thread** | Medium | Remove `time.sleep()` to ensure a responsive UI. |
| **Side Effects** | Medium | Separate the logic that updates the "mood" from the logic that retrieves the title string. |