- Code Smell Type: Global State / Tight Coupling
- Problem Location: `GLOBAL_STATE` dictionary and its usage across all functions (`init_data`, `increment_counter`, `toggle_flag`, `process_items`, `reset_state`).
- Detailed Explanation: The application relies on a single global mutable dictionary to manage state. This creates tight coupling between all functions and the global variable, making the code difficult to test in isolation (unit tests will interfere with each other), prone to side-effect bugs, and impossible to scale if multiple independent states are needed.
- Improvement Suggestions: Encapsulate the state within a class (e.g., `StateManager` or `AppState`). Pass the state object as an argument to functions or define the functions as methods within the class.
- Priority Level: High

- Code Smell Type: Magic Numbers
- Problem Location: `GLOBAL_STATE["threshold"]: 77` and `range(1, 21)` in `init_data`.
- Detailed Explanation: The number `77` and the range `1, 21` are "magic numbers"—hardcoded values without descriptive names. A developer reading the code cannot determine the business logic or significance behind these specific values, making maintenance risky.
- Improvement Suggestions: Define these values as named constants at the top of the module (e.g., `DEFAULT_THRESHOLD = 77`, `INITIAL_DATA_SIZE = 20`).
- Priority Level: Medium

- Code Smell Type: Violation of Single Responsibility Principle (SRP)
- Problem Location: `process_items()`
- Detailed Explanation: The `process_items` function is responsible for both iterating over the data and implementing the specific transformation logic based on the `flag` and `threshold`. As more conditions or transformation rules are added, this function will become a bloated "God function" that is hard to maintain.
- Improvement Suggestions: Extract the transformation logic into a separate strategy function or a mapping. For example, create a `transform_item(item, flag, threshold)` function that handles the logic for a single element.
- Priority Level: Low