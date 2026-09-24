### Code Review

**Naming Conventions**
*   `GLOBAL_THING`: Vague and non-descriptive. Rename to something reflecting its purpose, such as `APP_STATE`.
*   `do_periodic_stuff`: Non-descriptive function name. Rename to `update_ui_periodically` or similar.
*   `compute_title`: The name suggests a calculation, but the function also modifies global state (side effect). Rename to `update_and_get_title`.

**Software Engineering Standards**
*   **Global State**: The use of a global dictionary (`GLOBAL_THING`) for application state makes the code harder to test and maintain. Move this state into the `MyWindow` class or a dedicated State manager class.
*   **Side Effects**: `compute_title` modifies state while returning a value. State updates should be separated from string formatting for better predictability.

**Logic & Correctness**
*   **UI Blocking**: `time.sleep(0.1)` inside `handle_click` is called on the main GUI thread. While short, sleeping on the main thread freezes the interface and should be avoided in PySide/PyQt applications.

**Readability & Consistency**
*   **Magic Numbers**: The timer interval `777` and the modulo checks (`5`, `7`) are magic numbers. Define them as named constants at the top of the file to clarify their intent.