- Code Smell Type: Shared Mutable State / Tight Coupling
- Problem Location: `calculate_average_scores()`, `filter_high_scores()`, `process_misc()`, and `main()`
- Detailed Explanation: All functions rely directly on the global `DATA` variable instead of receiving data as arguments. This creates tight coupling between the logic and the data structure, making the functions impossible to unit test with different datasets and difficult to reuse in other contexts.
- Improvement Suggestions: Pass the necessary data as parameters to each function (e.g., `def calculate_average_scores(users):`).
- Priority Level: High

- Code Smell Type: Deeply Nested Conditional Logic
- Problem Location: `process_misc()` and the `if DATA["config"]["mode"] == "X":` block in `main()`.
- Detailed Explanation: The nested `if/else` structures increase cognitive load and make the control flow harder to follow. In `process_misc`, the logic for determining "Large/Small" and "Even/Odd" is repeated across multiple branches.
- Improvement Suggestions: 
    1. In `process_misc`, use string formatting or a mapping to determine the label (e.g., `size = "Large" if val > threshold else "Small"`).
    2. In `main`, use guard clauses or a flatter structure to handle the configuration flags.
- Priority Level: Medium

- Code Smell Type: Magic Numbers
- Problem Location: `filter_high_scores()` (the value `40`) and `main()` (indices `[0]` and `[1]`).
- Detailed Explanation: The number `40` is a hard-coded threshold with no explanation of its meaning. Similarly, accessing `flags` by index `0` and `1` assumes a specific order and meaning that isn't documented, making the code brittle if the config structure changes.
- Improvement Suggestions: Define named constants at the top of the file (e.g., `SCORE_THRESHOLD = 40`) or move these values into the `DATA["config"]` section.
- Priority Level: Medium

- Code Smell Type: Unnecessary Work / Manual Implementation
- Problem Location: `calculate_average_scores()` (the `for s in scores` loop).
- Detailed Explanation: The code manually iterates to calculate a sum and average. While not a performance bottleneck here, it is less readable and more error-prone than using built-in Python functions.
- Improvement Suggestions: Use `sum(scores) / len(scores)` to replace the inner loop.
- Priority Level: Low