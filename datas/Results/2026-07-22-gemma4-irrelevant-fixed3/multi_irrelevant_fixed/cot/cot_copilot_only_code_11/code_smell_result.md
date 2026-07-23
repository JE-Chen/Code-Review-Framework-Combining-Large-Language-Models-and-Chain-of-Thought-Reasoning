- Code Smell Type: Tight Coupling (Global State Dependency)
- Problem Location: `calculate_average_scores()`, `filter_high_scores()`, `process_misc()`, and `main()`
- Detailed Explanation: All functions rely directly on the global `DATA` variable instead of receiving data as arguments. This makes the functions impossible to unit test in isolation, prevents them from being reused with different datasets, and creates hidden dependencies that make the code fragile and harder to maintain.
- Improvement Suggestions: Pass the necessary data as parameters to each function (e.g., `def calculate_average_scores(users):`).
- Priority Level: High

- Code Smell Type: Deeply Nested Conditionals (Arrow Anti-pattern)
- Problem Location: `process_misc()` and the `if DATA["config"]["mode"] == "X":` block in `main()`
- Detailed Explanation: The nested `if/else` structures in `process_misc` and `main` reduce readability and increase cognitive load. In `process_misc`, the logic for determining "Large/Small" and "Even/Odd" is repeated across multiple branches, leading to verbose and redundant code.
- Improvement Suggestions: 
    1. In `process_misc`, use string formatting or a mapping to determine the label (e.g., `size = "Large" if val > threshold else "Small"` and `parity = "Even" if val % 2 == 0 else "Odd"`).
    2. In `main`, use guard clauses or a flatter logic structure to handle the configuration flags.
- Priority Level: Medium

- Code Smell Type: Manual Implementation of Standard Library Functions
- Problem Location: `calculate_average_scores()` (the `total` loop)
- Detailed Explanation: The code manually iterates through a list to calculate a sum and average. This is more verbose and error-prone than using built-in Python functions, which are more idiomatic and optimized.
- Improvement Suggestions: Use the built-in `sum()` function: `avg = sum(scores) / len(scores)`.
- Priority Level: Low

- Code Smell Type: Magic Numbers
- Problem Location: `filter_high_scores()` (`if s > 40:`)
- Detailed Explanation: The value `40` is a "magic number" with no explained context. It is unclear why 40 is the threshold for a "high score," and changing this value requires searching through the logic rather than updating a configuration constant.
- Improvement Suggestions: Define a named constant at the top of the file or include it in the `DATA["config"]` dictionary (e.g., `SCORE_THRESHOLD = 40`).
- Priority Level: Low