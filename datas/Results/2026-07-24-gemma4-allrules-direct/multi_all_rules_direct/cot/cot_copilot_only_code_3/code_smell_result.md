- Code Smell Type: Magic Numbers
- Problem Location: `if n % 2 == 0 and n != 0 and n > -9999:`
- Detailed Explanation: The value `-9999` is a magic number. It is unclear why this specific threshold exists or what business logic it represents. This makes the code difficult to maintain and modify if the requirement changes.
- Improvement Suggestions: Define a named constant at the top of the module (e.g., `MIN_VALID_NUMBER = -9999`) to provide semantic meaning to the value.
- Priority Level: Medium

- Code Smell Type: Deeply Nested Conditional Logic
- Problem Location: `step6_print_all` function
- Detailed Explanation: The function uses nested `if/else` blocks to handle string validation and printing. This increases cognitive load and makes the control flow harder to follow.
- Improvement Suggestions: Use guard clauses to handle the "Empty string" case early and return or continue, flattening the remaining logic.
- Priority Level: Low

- Code Smell Type: Unnecessary Work / Redundant Logic
- Problem Location: `step7_redundant_summary` function
- Detailed Explanation: The function manually iterates through a list to count elements, which is a built-in capability of Python. This is an inefficient implementation of a simple operation.
- Improvement Suggestions: Replace the loop with the built-in `len()` function: `return f"Total items: {len(strings)}"`.
- Priority Level: Low

- Code Smell Type: Poor Naming Conventions
- Problem Location: `step1_get_numbers`, `step2_filter_even`, etc.
- Detailed Explanation: Prefixing function names with `stepN_` describes the sequence of execution rather than the purpose of the function. If the order of operations changes, the names become misleading or require renaming across the codebase.
- Improvement Suggestions: Rename functions based on their responsibility (e.g., `get_initial_numbers`, `filter_even_numbers`, `duplicate_elements`).
- Priority Level: Medium