- Code Smell Type: Global State / Tight Coupling
- Problem Location: `GLOBAL_THING` dictionary and its usage across `compute_title`, `handle_click`, `generate_text`, and `main`.
- Detailed Explanation: The application relies on a mutable global dictionary to track state. This creates tight coupling between the logic and the global scope, making the code difficult to test in isolation, prone to side-effect bugs, and impossible to scale if multiple windows were ever needed.
- Improvement Suggestions: Encapsulate the state within the `MyWindow` class as instance attributes (e.g., `self.clicks`, `self.mood`, `self.start_time`) or create a dedicated `AppState` data class.
- Priority Level: High

- Code Smell Type: Blocking the Main UI Thread
- Problem Location: `time.sleep(0.1)` inside `handle_click`.
- Detailed Explanation: Calling `time.sleep()` in a GUI event handler freezes the entire application's main thread. While 0.1s is short, this pattern leads to "Not Responding" states and poor user experience as the UI cannot process paint events or other inputs during the sleep.
- Improvement Suggestions: Remove the `sleep` call. If a delay is required for logic, use `QTimer.singleShot` or a similar asynchronous mechanism.
- Priority Level: High

- Code Smell Type: Unclear/Non-Descriptive Naming
- Problem Location: `GLOBAL_THING`, `do_periodic_stuff`, `compute_title`.
- Detailed Explanation: Names like `GLOBAL_THING` and `do_periodic_stuff` are generic and provide no semantic meaning regarding the purpose of the data or the function. This forces developers to read the implementation details to understand the intent.
- Improvement Suggestions: Rename `GLOBAL_THING` to `app_state`, `do_periodic_stuff` to `update_ui_elements`, and `compute_title` to `update_window_title`.
- Priority Level: Medium

- Code Smell Type: Magic Numbers
- Problem Location: `self.timer.start(777)`, `random.random() < 0.3`, `GLOBAL_THING["clicks"] % 7 == 1`.
- Detailed Explanation: The use of hardcoded literals (777, 0.3, 7) without context makes the business logic opaque. It is unclear why the timer runs at that specific interval or why the modulo 7 trigger exists.
- Improvement Suggestions: Define these as named constants at the top of the file or within the class (e.g., `TIMER_INTERVAL_MS = 777`, `UI_UPDATE_CHANCE = 0.3`).
- Priority Level: Low