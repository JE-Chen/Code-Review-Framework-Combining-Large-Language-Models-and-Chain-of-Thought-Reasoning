- Code Smell Type: Tight Coupling / Global State Dependency
- Problem Location: `GLOBAL_STATE` dictionary and its usage across all functions (`init_data`, `increment_counter`, `toggle_flag`, `process_items`, `reset_state`).
- Detailed Explanation: The entire application relies on a single global mutable dictionary. This creates tight coupling between the functions and the state. It makes the code difficult to test (unit tests will interfere with each other), prevents thread safety, and makes it impossible to maintain multiple independent states within the same runtime. Any function can modify any part of the state at any time, leading to unpredictable side effects.
- Improvement Suggestions: Encapsulate the state within a class (e.g., `StateManager` or `AppState`). Pass the state object as an argument to functions or define the functions as methods within the class. This transforms the global state into an instance state.
- Priority Level: High

- Code Smell Type: Magic Numbers
- Problem Location: `GLOBAL_STATE["threshold"] = 77` and `range(1, 21)` in `init_data()`.
- Detailed Explanation: The number `77` and the range `21` are "magic numbers"—hardcoded values without descriptive names. A developer reading the code does not know why the threshold is 77 or why the data size is limited to 20. This reduces maintainability and makes updates error-prone.
- Improvement Suggestions: Define these values as named constants at the top of the file (e.g., `DEFAULT_THRESHOLD = 77` and `INITIAL_DATA_SIZE = 20`) to provide semantic meaning.
- Priority Level: Low

- Code Smell Type: Violation of Single Responsibility Principle (SRP)
- Problem Location: `process_items()`
- Detailed Explanation: The `process_items` function is handling two entirely different business logic paths based on the `flag` state (one path handles parity-based multiplication, the other handles threshold-based subtraction/addition). As the logic for either path grows, this function will become a "God Function" that is difficult to read and maintain.
- Improvement Suggestions: Extract the logic inside the `if GLOBAL_STATE["flag"]` and `else` blocks into separate helper functions (e.g., `_process_parity_logic()` and `_process_threshold_logic()`).
- Priority Level: Medium