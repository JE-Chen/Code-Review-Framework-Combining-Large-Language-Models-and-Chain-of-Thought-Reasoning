- Code Smell Type: Tight Coupling / Global State Dependency
- Problem Location: `GLOBAL_STATE` dictionary and its usage across all functions (`init_data`, `increment_counter`, `toggle_flag`, `process_items`, `reset_state`).
- Detailed Explanation: The entire application relies on a single global mutable dictionary. This creates tight coupling between the logic and the state, making the code difficult to test in isolation (unit tests will interfere with each other) and impossible to run in a multi-threaded environment without race conditions. It violates the principle of encapsulation.
- Improvement Suggestions: Encapsulate the state within a class (e.g., `AppState` or `StateManager`). Pass an instance of this class to the functions as an argument, or make the functions methods of the class.
- Priority Level: High

- Code Smell Type: Magic Numbers
- Problem Location: `GLOBAL_STATE["threshold"]: 77` and `range(1, 21)` in `init_data`.
- Detailed Explanation: The number `77` and the range `21` are "magic numbers"—hardcoded values without an explicit name or explanation. A developer reading the code cannot determine why `77` is the threshold or why the data size is limited to 20, making the code harder to maintain or adjust.
- Improvement Suggestions: Define these values as named constants at the top of the file (e.g., `DEFAULT_THRESHOLD = 77`, `INITIAL_DATA_SIZE = 20`).
- Priority Level: Medium

- Code Smell Type: Violation of Single Responsibility Principle (SRP)
- Problem Location: `process_items()`
- Detailed Explanation: The `process_items` function is responsible for both iterating through the data and implementing the specific business logic for two different modes (flagged vs. non-flagged). As more modes or conditions are added, this function will grow into a complex set of nested conditionals, making it fragile and hard to read.
- Improvement Suggestions: Extract the item processing logic into a separate function or use a strategy pattern where the processing logic is determined by the state of the flag before the loop begins.
- Priority Level: Low