- Code Smell Type: Long Parameter List & Unclear Naming
- Problem Location: `def doStuff(a, b, c, d, e, f, g, h, i, j):`
- Detailed Explanation: The function accepts 10 parameters with single-letter names. This makes the code nearly impossible to read or maintain without referring back to the call site. It violates the principle of semantic clarity and makes the function signature fragile.
- Improvement Suggestions: Group related parameters into a Data Transfer Object (DTO) or a dictionary. Rename variables to descriptive names (e.g., `a` $\rightarrow$ `value`, `b` $\rightarrow$ `shape_type`).
- Priority Level: High

- Code Smell Type: Deeply Nested Conditionals (Arrow Anti-pattern)
- Problem Location: The nested `if d: if e: if f: ...` block in `doStuff`.
- Detailed Explanation: The logic is nested five levels deep. This increases cognitive load, makes the code harder to test, and increases the likelihood of logic errors when modifying the conditions.
- Improvement Suggestions: Use guard clauses to return early or flatten the logic using a mapping/strategy pattern or a combined boolean expression.
- Priority Level: High

- Code Smell Type: Mutable Default Argument
- Problem Location: `def collectValues(x, bucket=[]):`
- Detailed Explanation: In Python, default arguments are evaluated once at definition time, not at execution time. The `bucket` list is shared across all calls to `collectValues`, leading to unexpected behavior where data persists between unrelated function calls (as seen in the `__main__` output).
- Improvement Suggestions: Use `bucket=None` as the default and initialize it inside the function: `if bucket is None: bucket = []`.
- Priority Level: High

- Code Smell Type: Use of Global State
- Problem Location: `global total_result` inside `doStuff`.
- Detailed Explanation: Modifying a global variable inside a function creates hidden dependencies and makes the code non-thread-safe and difficult to unit test in isolation.
- Improvement Suggestions: Pass the accumulator as an argument to the function or return the result and handle the summation in the calling function.
- Priority Level: Medium

- Code Smell Type: Magic Numbers & Redundant Logic
- Problem Location: `3.14159`, `2.71828` and the `temp1`/`temp2` calculations.
- Detailed Explanation: Hardcoded constants should be defined as named constants (e.g., `math.pi`). Additionally, the sequence `temp1 = z + 1; temp2 = temp1 - 1; result = temp2` is mathematically redundant and adds noise to the code.
- Improvement Suggestions: Use the `math` module for constants and remove the redundant arithmetic operations.
- Priority Level: Low

- Code Smell Type: Poor Type Handling & Generic Exception Catching
- Problem Location: `processEverything` loop and `except:` block.
- Detailed Explanation: Using `type(item) == int` is less flexible than `isinstance()`. More critically, the bare `except:` block catches all exceptions (including `KeyboardInterrupt`), which can hide bugs and make debugging difficult.
- Improvement Suggestions: Use `isinstance()` for type checking and catch specific exceptions (e.g., `ValueError`).
- Priority Level: Medium