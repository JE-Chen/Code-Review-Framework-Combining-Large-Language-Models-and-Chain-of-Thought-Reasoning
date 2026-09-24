- Code Smell Type: Shared Mutable State (Global State)
- Problem Location: `GLOBAL_STATE = { ... }` and its usage across all functions.
- Detailed Explanation: The code relies on a global dictionary to manage application state. This introduces hidden coupling between functions, making the code difficult to test in isolation and prone to side-effect bugs. If this code were to be used in a multi-threaded environment or integrated into a larger system, managing the state of `GLOBAL_STATE` would become a significant source of instability.
- Improvement Suggestions: Encapsulate the state within a class (e.g., `StateManager` or `AppState`) and pass an instance of that class to the functions that need it, or make the functions methods of that class.
- Priority Level: High

- Code Smell Type: Deeply Nested Conditional Logic
- Problem Location: `process_items()` function.
- Detailed Explanation: The function uses nested `if/else` blocks to determine how to process items. This increases cognitive load and makes the logic harder to follow. As more conditions are added (e.g., more modes or flags), the complexity will grow quadratically.
- Improvement Suggestions: Use guard clauses or extract the item-processing logic into a separate strategy function. For example, create a helper function `calculate_item_value(item, flag, threshold)` to flatten the loop.
- Priority Level: Medium

- Code Smell Type: Magic Numbers
- Problem Location: `GLOBAL_STATE["threshold"]: 77` and `range(1, 21)`.
- Detailed Explanation: The number `77` and the range `1, 21` are hard-coded without explanation. A developer reading the code cannot determine why these specific values were chosen or what they represent in a business context.
- Improvement Suggestions: Define these as named constants at the top of the module (e.g., `DEFAULT_THRESHOLD = 77`, `INITIAL_DATA_SIZE = 20`) to provide semantic meaning.
- Priority Level: Low