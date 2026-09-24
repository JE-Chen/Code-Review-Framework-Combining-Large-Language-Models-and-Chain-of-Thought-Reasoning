### Code Review

**Naming Conventions**
*   **`doSomething`**: The function name is vague. It should describe the actual purpose of the calculation.
*   **`a, b, c, d, e, f, g, h, i, j`**: These parameter names are non-descriptive. Use meaningful names that reflect the data they represent.
*   **`x`, `y`, `val`**: These variable names are too generic. Use descriptive names (e.g., `total_sum` instead of `x`).

**Readability & Consistency**
*   **Deep Nesting**: `doSomething` and `main` contain deeply nested `if` statements (arrow code). Use guard clauses (early returns) to flatten the logic and improve readability.
*   **Unused Parameters**: Parameters `g, h, i, j` in `doSomething` are never used. Remove them to clean up the function signature.

**Software Engineering Standards**
*   **Hardcoded Magic Numbers**: Values like `999999`, `1234`, and `123456789` are "magic numbers." Define them as named constants at the top of the file to provide context.
*   **Looping Pattern**: In `processData`, using `for k in range(len(dataList))` is an anti-pattern in Python. Iterate directly over the elements: `for item in dataList:`.

**Logic & Correctness**
*   **Division by Zero Handling**: While there is a check for `d != 0`, returning a magic number (`999999`) as an error indicator is fragile. Consider raising a specific exception or returning `None`.

**Suggested Improvements**
*   **Refactor `doSomething`**: Replace nested `if` blocks with `elif` or return statements.
*   **Refactor `processData`**: Use a generator expression with `sum()` for a more idiomatic approach:
    `return sum(item * 2 if item % 2 == 0 else item * 3 for item in dataList)`