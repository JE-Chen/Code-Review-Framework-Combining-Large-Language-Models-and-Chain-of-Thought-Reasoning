- Code Smell Type: Global State / Tight Coupling
- Problem Location: `GLOBAL_THING` dictionary and its usage across `compute_title`, `handle_click`, `generate_text`, and `main`.
- Detailed Explanation: The application relies on a global mutable dictionary to track state (`clicks`, `mood`, `started`). This creates tight coupling between the `MyWindow` class and the global scope, making the code difficult to test in isolation, prone to side-effect bugs, and impossible to scale if multiple windows were needed.
- Improvement Suggestions: Encapsulate the state within the `MyWindow` class as instance attributes (e.g., `self.clicks`, `self.mood`, `self.start_time`) or create a dedicated `AppState` data class that is passed into the window via dependency injection.
- Priority Level: High

- Code Smell Type: Blocking the Main UI Thread
- Problem Location: `time.sleep(0.1)` inside `handle_click`.
- Detailed Explanation: Calling `time.sleep()` in a GUI application freezes the event loop. While 0.1 seconds is short, it causes the interface to stutter (dropped frames) and is a dangerous pattern. In a larger application, this leads to "Application Not Responding" (ANR) errors.
- Improvement Suggestions: Remove the `sleep` call. If a delay is intentionally required for logic, use `QTimer.singleShot()` or a separate worker thread to avoid blocking the main thread.
- Priority Level: High

- Code Smell Type: Unclear/Non-Descriptive Naming
- Problem Location: `GLOBAL_THING`, `do_periodic_stuff`, `compute_title`.
- Detailed Explanation: Names like `GLOBAL_THING` and `do_periodic_stuff` are generic and provide no semantic meaning regarding the purpose of the data or the function. This forces developers to read the implementation details to understand the intent, reducing maintainability.
- Improvement Suggestions: Rename `GLOBAL_THING` to `app_state` or `session_data`. Rename `do_periodic_stuff` to `update_ui_randomly` or `refresh_dynamic_content`.
- Priority Level: Medium

- Code Smell Type: Magic Numbers
- Problem Location: `self.timer.start(777)`, `random.random() < 0.3`, `GLOBAL_THING["clicks"] % 7 == 1`.
- Detailed Explanation: The values `777`, `0.3`, and `7` are "magic numbers"—hardcoded constants without explanation. It is unclear why the timer is set to exactly 777ms or why the probability is 30%.
- Improvement Suggestions: Define these as named constants at the top of the file or within the class (e.g., `REFRESH_INTERVAL_MS = 777`, `UI_UPDATE_CHANCE = 0.3`).
- Priority Level: Low