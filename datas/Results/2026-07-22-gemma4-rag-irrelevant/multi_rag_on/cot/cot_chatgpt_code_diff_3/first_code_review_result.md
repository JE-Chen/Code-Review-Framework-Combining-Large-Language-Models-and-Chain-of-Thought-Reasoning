### Code Review

**Naming Conventions**
* **`GLOBAL_THING`**: Vague and non-descriptive. Rename to something reflecting its purpose, such as `AppState` or `SessionData`.
* **`do_periodic_stuff`**: Non-descriptive. Rename to reflect the actual behavior, e.g., `update_ui_randomly`.
* **`compute_title`**: The name suggests a calculation, but the function also modifies global state (`mood`). This is a side effect that should be reflected in the name or separated.

**Software Engineering Standards**
* **Global State**: The use of a global dictionary (`GLOBAL_THING`) for application state makes the code harder to test and maintain. This state should be encapsulated within the `MyWindow` class or a dedicated State manager class.
* **Side Effects**: `compute_title` modifies state while returning a value. This violates the principle of command-query separation.

**Logic & Correctness**
* **UI Blocking**: `time.sleep(0.1)` inside `handle_click` is called on the main GUI thread. While 100ms is short, sleeping on the main thread freezes the UI and should be avoided in PySide/PyQt applications.

**Readability & Consistency**
* **Formatting**: The code is generally well-formatted and follows PEP 8 standards.
* **Strings**: The UI text ("Hello but why", "Click maybe") is informal; ensure this aligns with the intended product requirements.