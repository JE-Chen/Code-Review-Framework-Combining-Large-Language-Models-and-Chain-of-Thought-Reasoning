- Code Smell Type: Tight Coupling (Global State Dependency)
- Problem Location: `calculate_average_scores()`, `filter_high_scores()`, `process_misc()`, and `main()`
- Detailed Explanation: All functions rely directly on the global `DATA` variable instead of receiving data as arguments. This makes the functions impossible to unit test in isolation, prevents them from being reused with different datasets, and creates hidden dependencies that make the code fragile and harder to maintain.
- Improvement Suggestions: Pass the required data as parameters to each function (e.g., `def calculate_average_scores(users):`).
- Priority Level: High

- Code Smell Type: Deeply Nested Conditionals (Arrow Anti-pattern)
- Problem Location: `process_misc()` and the `if DATA["config"]["mode"] == "X"` block in `main()`.
- Detailed Explanation: The nested `if/else` structures in `process_misc` and `main` reduce readability and increase cognitive load. In `process_misc`, the logic for determining "Large/Small" and "Even/Odd" is repeated across multiple branches, making the flow harder to follow.
- Improvement Suggestions: 
    1. In `process_misc`, use string formatting or a mapping to determine the label (e.g., `size = "Large" if val > threshold else "Small"`).
    2. In `main`, use guard clauses or a flatter logic structure to handle the flags.
- Priority Level: Medium

- Code Smell Type: Manual Implementation of Standard Library Functions
- Problem Location: `calculate_average_scores()` (the `total` loop)
- Detailed Explanation: The code manually iterates through a list to calculate a sum and then divides by the length. Python provides built-in functions like `sum()` and `len()` (or the `statistics` module) that are more concise, idiomatic, and generally more performant.
- Improvement Suggestions: Replace the inner `for s in scores` loop with `avg = sum(scores) / len(scores)`.
- Priority Level: Low