### Code Review

**Naming Conventions**
* **Vague Naming**: `GLOBAL_THING`, `do_periodic_stuff`, and `compute_title` are non-descriptive. Use names that reflect the actual purpose (e.g., `APP_STATE`, `update_ui_periodically`, `generate_window_title`).
* **Unclear UI Text**: Label and button text ("Hello but why", "Click maybe") are cryptic and lack professional clarity.

**Software Engineering Standards**
* **Shared Mutable State**: The use of `GLOBAL_THING` as a global dictionary introduces hidden coupling and makes the code harder to test. This state should be encapsulated within the `MyWindow` class or a dedicated state management object.
* **Single Responsibility**: `compute_title` both modifies the application state (`mood`) and returns a string. These responsibilities should be separated.

**Logic & Correctness**
* **Blocking the UI Thread**: `time.sleep(0.1)` inside `handle_click` blocks the main GUI thread. Even a short sleep can cause the interface to stutter or freeze; use `QTimer` or asynchronous patterns if delays are necessary.

**Performance & Security**
* **Magic Numbers**: The values `777`, `0.3`, `5`, and `7` are hard-coded magic numbers. Move these to named constants at the top of the file to improve maintainability.

**Readability & Consistency**
* **Formatting**: There is an unnecessary double newline between `__init__` and `compute_title`.