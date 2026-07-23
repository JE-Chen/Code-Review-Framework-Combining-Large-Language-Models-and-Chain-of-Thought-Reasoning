- Code Smell Type: Tight Coupling / Global State Dependency
- Problem Location: `GLOBAL_STATE` and its usage across `init_data`, `increment_counter`, `toggle_flag`, `process_items`, and `reset_state`.
- Detailed Explanation: The entire application relies on a single global dictionary. This creates tight coupling between the functions and the state, making the code difficult to test in isolation (unit tests will interfere with each other) and impossible to use in a multi-threaded or concurrent environment without race conditions. It violates the principle of encapsulation.
- Improvement Suggestions: Encapsulate the state within a class (e.g., `StateManager` or `AppState`) and pass an instance of this class to the functions, or make the functions methods of that class.
- Priority Level: High

- Code Smell Type: Magic Numbers
- Problem Location: `GLOBAL_STATE["threshold"]: 77` and `range(1, 21)` in `init_data`.
- Detailed Explanation: The number `77` and the range `1, 21` are "magic numbers"—hardcoded values with no explained meaning. If these values need to change or are used elsewhere, it becomes difficult to maintain and understand the business logic behind these specific thresholds.
- Improvement Suggestions: Define these values as named constants at the top of the module (e.g., `DEFAULT_THRESHOLD = 77`, `INITIAL_DATA_LIMIT = 20`) to provide semantic meaning.
- Priority Level: Medium

- Code Smell Type: Violation of Single Responsibility Principle (SRP)
- Problem Location: `process_items()`
- Detailed Explanation: The `process_items` function is handling two entirely different business logic paths based on the `flag` state (one path handles parity-based multiplication, the other handles threshold-based subtraction/addition). As the logic for either path grows, this function will become a bloated "God function" that is hard to maintain.
- Improvement Suggestions: Extract the logic inside the `if GLOBAL_STATE["flag"]` and `else` blocks into separate helper functions (e.g., `_process_parity_logic()` and `_process_threshold_logic()`).
- Priority Level: Low