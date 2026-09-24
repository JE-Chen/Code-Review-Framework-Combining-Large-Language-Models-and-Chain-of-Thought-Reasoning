- Code Smell Type: Unclear Naming & Long Parameter List
- Problem Location: `def doStuff(a, b, c, d, e, f, g, h, i, j):`
- Detailed Explanation: The function uses single-letter variable names for all parameters and local variables. This provides zero semantic context, making the logic nearly impossible to understand without tracing every line. Furthermore, passing 10 parameters (many of which are flags) indicates a violation of the Single Responsibility Principle and creates a rigid, fragile interface.
- Improvement Suggestions: Rename variables to reflect their purpose (e.g., `a` $\rightarrow$ `value`, `b` $\rightarrow$ `shape_type`). Group related flags into a configuration object or a dataclass to reduce the parameter count.
- Priority Level: High

- Code Smell Type: Deeply Nested Conditionals (Arrow Anti-pattern)
- Problem Location: The nested `if d: if e: if f: ...` block in `doStuff`.
- Detailed Explanation: The code reaches five levels of indentation to determine the value of `z`. This significantly harms readability and increases the cognitive load required to understand the execution flow. It also makes the function difficult to test, as every permutation of flags must be considered.
- Improvement Suggestions: Use guard clauses to return early or flatten the logic using a mapping/strategy pattern. Combine boolean conditions using logical operators (e.g., `if d and e and f and g and h:`) to reduce nesting.
- Priority Level: High

- Code Smell Type: Mutable Default Argument
- Problem Location: `def collectValues(x, bucket=[]):`
- Detailed Explanation: In Python, default arguments are evaluated once at definition time, not at call time. The `bucket` list is shared across all calls to `collectValues` that do not provide their own list. This leads to unexpected behavior where data persists between unrelated function calls (as seen in the `__main__` output).
- Improvement Suggestions: Use `bucket=None` as the default value and initialize it inside the function: `if bucket is None: bucket = []`.
- Priority Level: High

- Code Smell Type: Global State Dependency
- Problem Location: `global total_result` inside `doStuff`.
- Detailed Explanation: Modifying a global variable inside a utility function creates hidden side effects. This makes the code harder to debug, prevents thread safety, and makes unit testing difficult because the state persists across tests.
- Improvement Suggestions: Pass the accumulator as an argument to the function or return the result and handle the summation in the calling function (`processEverything`).
- Priority Level: Medium

- Code Smell Type: Magic Numbers & Redundant Logic
- Problem Location: `3.14159`, `2.71828`, and the `temp1`/`temp2` calculations.
- Detailed Explanation: Hardcoded constants should be replaced with named constants or library calls (e.g., `math.pi`). Additionally, the sequence `temp1 = z + 1; temp2 = temp1 - 1; result = temp2` is mathematically redundant and adds noise to the code.
- Improvement Suggestions: Use `math.pi` and `math.e`. Remove the redundant `temp` variables and assign `result = z` directly.
- Priority Level: Low