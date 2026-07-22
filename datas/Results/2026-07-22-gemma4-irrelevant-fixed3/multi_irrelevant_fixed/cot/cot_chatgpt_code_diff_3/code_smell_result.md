- Code Smell Type: Global State / Tight Coupling
- Problem Location: `GLOBAL_THING` dictionary and its usage across `compute_title`, `handle_click`, `generate_text`, and `main`.
- Detailed Explanation: The application relies on a global mutable dictionary to manage state. This creates tight coupling between the logic and the global scope, making the code difficult to test in isolation, prone to side-effect bugs, and impossible to scale if multiple windows or instances of `MyWindow` were needed.
- Improvement Suggestions: Encapsulate the state within the `MyWindow` class as instance attributes (e.g., `self.clicks`, `self.mood`, `self.start_time`) or create a dedicated `AppState` class to manage the data.
- Priority Level: High

- Code Smell Type: Blocking the Main UI Thread
- Problem Location: `time.sleep(0.1)` inside `handle_click`.
- Detailed Explanation: Calling `time.sleep()` in a GUI event handler freezes the entire application's event loop. Even a short delay (100ms) can cause noticeable stuttering or "Not Responding" states in the UI, degrading the user experience.
- Improvement Suggestions: Remove the `sleep` call. If a delay is intentionally required for logic, use `QTimer.singleShot()` or a separate worker thread to avoid blocking the main thread.
- Priority Level: High

- Code Smell Type: Unclear Naming
- Problem Location: `GLOBAL_THING`, `do_periodic_stuff`, `compute_title`.
- Detailed Explanation: The names are generic and non-descriptive. `GLOBAL_THING` does not describe what the data represents; `do_periodic_stuff` does not explain the purpose of the periodic update. This forces developers to read the implementation details to understand the intent.
- Improvement Suggestions: Rename `GLOBAL_THING` to `app_state` or `session_data`. Rename `do_periodic_stuff` to `update_ui_randomly` or `refresh_status`. Rename `compute_title` to `update_window_title`.
- Priority Level: Medium

- Code Smell Type: Magic Numbers
- Problem Location: `self.timer.start(777)`, `random.random() < 0.3`, `GLOBAL_THING["clicks"] % 7 == 1`.
- Detailed Explanation: The use of hardcoded literals (777, 0.3, 7) without context makes the business logic opaque. It is unclear why the timer runs at that specific interval or why the modulo 7 trigger exists.
- Improvement Suggestions: Extract these values into named constants at the top of the file or within the class (e.g., `REFRESH_INTERVAL_MS = 777`, `RANDOM_UPDATE_CHANCE = 0.3`).
- Priority Level: Low