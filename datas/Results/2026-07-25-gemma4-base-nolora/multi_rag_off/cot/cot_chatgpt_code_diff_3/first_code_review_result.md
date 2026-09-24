### Code Review

**Naming Conventions**
*   `GLOBAL_THING`: Vague and non-descriptive. Suggest renaming to `APP_STATE` or `SessionData`.
*   `do_periodic_stuff`: Non-descriptive function name. Suggest `update_ui_randomly` or `refresh_periodic_state`.
*   `compute_title`: The name implies a calculation, but it also modifies global state (side effect). Suggest `update_and_get_title`.

**Software Engineering Standards**
*   **Global State**: The use of a global dictionary (`GLOBAL_THING`) for application state makes the code harder to test and maintain. This state should be encapsulated within the `MyWindow` class or a dedicated State manager class.
*   **Side Effects**: `compute_title` modifies the state of the application while appearing to be a getter. This violates the principle of command-query separation.

**Logic & Correctness**
*   **UI Blocking**: `time.sleep(0.1)` inside `handle_click` is called on the main GUI thread. While 100ms is short, calling `sleep` in a PySide/PyQt event loop freezes the entire interface and should be avoided.

**Readability & Consistency**
*   **Formatting**: The code is generally well-formatted and follows PEP 8 standards.
*   **Comments**: The code lacks docstrings or comments explaining the purpose of the periodic timer or the logic behind the modulo-based text changes.

**Performance & Security**
*   No significant performance bottlenecks or security risks identified for a script of this scale.