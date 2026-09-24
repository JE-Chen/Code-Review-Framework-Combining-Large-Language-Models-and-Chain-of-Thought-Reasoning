- Code Smell Type: Tight Coupling (Global State Dependency)
- Problem Location: `calculate_average_scores()`, `filter_high_scores()`, `process_misc()`, and `main()`
- Detailed Explanation: All functions rely directly on the global `DATA` variable instead of receiving data as arguments. This makes the functions impossible to unit test in isolation, prevents them from being reused with different datasets, and creates hidden dependencies that make the code fragile and harder to maintain.
- Improvement Suggestions: Refactor functions to accept the necessary data as parameters. For example: `def calculate_average_scores(users):`.
- Priority Level: High

- Code Smell Type: Magic Numbers / Hardcoded Logic
- Problem Location: `filter_high_scores()` (line: `if s > 40:`)
- Detailed Explanation: The value `40` is a "magic number." It is unclear where this threshold comes from or what it represents. If this threshold needs to change, a developer must hunt through the logic to find it. Given that a `threshold` already exists in `DATA["config"]`, this is inconsistent.
- Improvement Suggestions: Move the value `40` to a named constant or use the existing `DATA["config"]["threshold"]` if that is the intended logic.
- Priority Level: Medium

- Code Smell Type: Deeply Nested Conditionals (Arrow Anti-pattern)
- Problem Location: `process_misc()` and the `if DATA["config"]["mode"] == "X":` block in `main()`.
- Detailed Explanation: The code uses nested `if/else` blocks to handle combinations of parity and size (in `process_misc`) and flag checks (in `main`). This increases cognitive load and makes the logic harder to follow and extend.
- Improvement Suggestions: 
    1. In `process_misc`, use string formatting or a mapping to determine the label (e.g., `size = "Large" if val > threshold else "Small"`).
    2. In `main`, use guard clauses or a more flattened logic structure to handle the flags.
- Priority Level: Medium

- Code Smell Type: Reinventing the Wheel (Manual Accumulation)
- Problem Location: `calculate_average_scores()` (lines: `total = 0`, `for s in scores: total += s`)
- Detailed Explanation: The code manually iterates to sum a list, which is less readable and more error-prone than using built-in Python functions.
- Improvement Suggestions: Use the built-in `sum()` function: `avg = sum(scores) / len(scores)`.
- Priority Level: Low