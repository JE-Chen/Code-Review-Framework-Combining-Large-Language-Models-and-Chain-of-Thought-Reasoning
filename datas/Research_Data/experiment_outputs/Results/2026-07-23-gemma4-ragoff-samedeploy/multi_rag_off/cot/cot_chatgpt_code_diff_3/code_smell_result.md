- Code Smell Type: Global State / Tight Coupling
- Problem Location: `GLOBAL_THING` dictionary and its usage across `MyWindow` and `main()`.
- Detailed Explanation: The application relies on a global mutable dictionary to track state (`clicks`, `mood`, `started`). This creates tight coupling between the UI logic and the data layer, making the code difficult to test in isolation, prone to side-effect bugs, and impossible to scale if multiple windows or instances were needed.
- Improvement Suggestions: Encapsulate the state within a dedicated `AppState` class or move the state variables directly into the `MyWindow` class as instance attributes (e.g., `self.clicks`, `self.mood`).
- Priority Level: High

- Code Smell Type: Blocking the Main UI Thread
- Problem Location: `time.sleep(0.1)` inside `handle_click`.
- Detailed Explanation: Calling `time.sleep()` on the main thread of a GUI application freezes the event loop. While 0.1s is short, it causes a perceptible stutter in the user interface and is a dangerous pattern that leads to "Application Not Responding" (ANR) errors as complexity grows.
- Improvement Suggestions: Remove the sleep call. If a delay is required for logic, use `QTimer.singleShot()` or a separate worker thread via `QThread`.
- Priority Level: High

- Code Smell Type: Unclear/Non-Descriptive Naming
- Problem Location: `GLOBAL_THING`, `do_periodic_stuff`, `compute_title`.
- Detailed Explanation: Names like `GLOBAL_THING` and `do_periodic_stuff` are generic and provide no semantic meaning regarding the purpose of the data or the function. This forces developers to read the implementation details to understand the intent, reducing maintainability.
- Improvement Suggestions: Rename `GLOBAL_THING` to `app_state`, `do_periodic_stuff` to `update_ui_randomly`, and `compute_title` to `update_window_title`.
- Priority Level: Medium

- Code Smell Type: Magic Numbers
- Problem Location: `self.timer.start(777)`, `random.random() < 0.3`, `GLOBAL_THING["clicks"] % 7 == 1`.
- Detailed Explanation: The use of hardcoded literals (777, 0.3, 7) without context makes the business logic opaque. It is unclear why the timer runs every 777ms or why the 7th click triggers a specific label change.
- Improvement Suggestions: Define these as named constants at the top of the file or within the class (e.g., `UPDATE_INTERVAL_MS = 777`, `RANDOM_UPDATE_CHANCE = 0.3`).
- Priority Level: Low