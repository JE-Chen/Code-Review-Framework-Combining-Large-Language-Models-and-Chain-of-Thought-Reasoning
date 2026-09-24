- Code Smell Type: Shared Mutable State (Global State)
- Problem Location: `GLOBAL_STATE = { ... }` and its usage across `init_data`, `increment_counter`, `toggle_flag`, `process_items`, and `reset_state`.
- Detailed Explanation: The code relies on a global dictionary to manage application state. This introduces hidden coupling between all functions in the module. It makes the code difficult to test in isolation (unit tests will interfere with each other unless the state is manually reset), prevents thread safety, and makes it nearly impossible to run multiple independent instances of this logic within the same process. This directly violates the provided RAG rule regarding shared mutable state.
- Improvement Suggestions: Encapsulate the state within a class (e.g., `StateManager` or `AppState`). Pass an instance of this class to the functions that need it, or make the functions methods of that class.
- Priority Level: High

- Code Smell Type: Magic Numbers
- Problem Location: `GLOBAL_STATE["threshold"]: 77` and `range(1, 21)` in `init_data`.
- Detailed Explanation: The number `77` and the range `1, 21` are "magic numbers"—hardcoded values with no explained meaning. A developer reading the code cannot determine why the threshold is 77 or why the data size is limited to 20, making the code harder to maintain or adjust.
- Improvement Suggestions: Define these values as named constants at the top of the file (e.g., `DEFAULT_THRESHOLD = 77` and `INITIAL_DATA_SIZE = 20`) to provide semantic meaning.
- Priority Level: Low

- Code Smell Type: Violation of Single Responsibility Principle (SRP)
- Problem Location: `process_items()`
- Detailed Explanation: The `process_items` function is responsible for both iterating over the data and implementing the business logic for two entirely different processing modes (determined by the `flag`). As more modes or conditions are added, this function will grow into a complex set of nested conditionals, making it fragile and hard to read.
- Improvement Suggestions: Extract the logic inside the loop into a separate strategy function or a mapping. For example, create a `calculate_item_value(item, flag, threshold)` function to separate the "how to process" from the "what to iterate."
- Priority Level: Medium