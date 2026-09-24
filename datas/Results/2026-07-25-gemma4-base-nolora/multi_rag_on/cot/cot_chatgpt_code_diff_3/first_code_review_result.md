### Code Review

**Naming Conventions**
* **Vague Naming**: `GLOBAL_THING`, `do_periodic_stuff`, and `compute_title` are non-descriptive. Use names that reflect the actual purpose (e.g., `AppState`, `update_ui_periodically`, `update_window_title`).
* **Cryptic UI Text**: Label and button text ("Hello but why", "Click maybe") are unprofessional/vague; ensure UI strings are meaningful to the user.

**Software Engineering Standards & RAG Rules**
* **Shared Mutable State**: The use of `GLOBAL_THING` as a global dictionary introduces hidden coupling. This state should be encapsulated within a class (e.g., a `State` object) and passed to `MyWindow`.
* **Magic Numbers**: The values `777` (timer interval), `0.3` (probability), and `7` (modulo check) are magic numbers. Move these to named constants at the top of the file.

**Logic & Correctness**
* **Blocking the UI Thread**: `time.sleep(0.1)` inside `handle_click` blocks the main GUI thread. While short, this is bad practice in PySide/PyQt and can lead to "Not Responding" states. Remove the sleep or use a non-blocking approach.

**Readability & Consistency**
* **Formatting**: There is an unnecessary double newline between `__init__` and `compute_title`.

**Summary of Suggestions**
* Replace `GLOBAL_THING` with a state management class.
* Rename functions and variables to be semantically clear.
* Extract hard-coded numbers into constants.
* Remove `time.sleep()` from the event handler.