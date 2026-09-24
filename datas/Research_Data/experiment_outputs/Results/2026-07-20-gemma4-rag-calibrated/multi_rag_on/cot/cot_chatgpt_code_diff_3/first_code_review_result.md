### Code Review

**Naming Conventions**
* `GLOBAL_THING` is too vague. Use a more descriptive name like `APP_STATE` or `SessionState`.
* `do_periodic_stuff` and `compute_title` are imprecise. Consider `update_periodic_ui` and `get_window_title`.

**Software Engineering Standards & RAG Rules**
* **Shared Mutable State:** The use of `GLOBAL_THING` as a module-level dictionary introduces hidden coupling. This state should be encapsulated within the `MyWindow` class or a dedicated state management object.
* **Magic Numbers:** The values `777` (timer interval), `0.3` (probability), and `5`/`7` (modulo checks) are magic numbers. Move these to named constants at the top of the file.

**Logic & Correctness**
* **UI Blocking:** `time.sleep(0.1)` inside `handle_click` blocks the main GUI thread. While short, this is bad practice in PySide/PyQt; use `QTimer` or avoid sleeping in event handlers.

**Readability & Consistency**
* The string literals in `QLabel` and `QPushButton` ("Hello but why", "Click maybe") are inconsistent in tone and lack clarity regarding the app's purpose.