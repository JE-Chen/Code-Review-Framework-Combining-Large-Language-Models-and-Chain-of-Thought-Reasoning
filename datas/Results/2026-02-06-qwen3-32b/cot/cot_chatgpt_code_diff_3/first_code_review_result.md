- **Critical UI Blocking Issue**  
  `time.sleep(0.1)` in `handle_click` freezes the entire GUI every 5 clicks. Replace with non-blocking logic (e.g., `QTimer` for delayed actions) to prevent unresponsive UI.

- **Global State Abuse**  
  `GLOBAL_THING` violates encapsulation. Move state (clicks, mood, started) into `MyWindow` class properties. Globals create hidden dependencies and complicate testing.

- **Vague Naming**  
  `GLOBAL_THING` is unclear. Rename to `APP_STATE` if unavoidable, but prefer encapsulation. `mood` key lacks semantic context (e.g., use `MoodState` enum).

- **Inconsistent Logic**  
  `generate_text()` uses `uptime` but `compute_title()` mutates `GLOBAL_THING["mood"]` directly. Decouple state from UI updates for predictability.

- **Missing Documentation**  
  Add docstrings for class/methods (e.g., explain `GLOBAL_THING` usage or state transitions). Comments should clarify *why*, not *what*.

- **Unnecessary Global Mutation**  
  `compute_title()` alters `GLOBAL_THING` instead of returning a value. This creates side effects; compute title *within* `MyWindow` without global access.

- **Confusing Condition**  
  `GLOBAL_THING["clicks"] % 7 == 1` in `do_periodic_stuff` is ambiguous. Use descriptive condition (e.g., `if clicks % 7 == 1 and clicks > 0:`) or extract to helper.

- **Potential Race Condition**  
  Global state accessed from multiple threads (e.g., `do_periodic_stuff` timer). Ensure thread safety via Qt signals or `QMutex` if extending.