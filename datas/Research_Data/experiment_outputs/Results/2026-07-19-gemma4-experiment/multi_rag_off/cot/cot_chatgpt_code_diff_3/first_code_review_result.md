### Code Review

**Naming Conventions**
* `GLOBAL_THING`: Vague and non-descriptive. Suggest renaming to `AppState` or `SessionData` to reflect its purpose.
* `do_periodic_stuff`: Non-descriptive. Suggest `update_ui_randomly` or `refresh_periodic_state`.
* `compute_title`: The name implies a calculation, but it also modifies global state (side effect). Suggest `update_and_get_title`.

**Software Engineering Standards**
* **Global State**: The use of a global dictionary (`GLOBAL_THING`) for application state makes the code harder to test and maintain. Suggest moving this state into the `MyWindow` class or a dedicated State manager class.

**Logic & Correctness**
* **UI Blocking**: `time.sleep(0.1)` inside `handle_click` is called on the main GUI thread. While short, sleeping on the main thread freezes the event loop and should be avoided in PySide/PyQt applications.

**Readability & Consistency**
* The code is generally well-formatted and follows PEP 8 standards.