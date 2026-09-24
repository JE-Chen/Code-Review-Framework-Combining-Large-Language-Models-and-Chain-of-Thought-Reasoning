### Code Review

**1. Naming Conventions**
*   **Vague Naming:** `doStuff` and `processEverything` are non-descriptive. Use names that reflect the actual business logic (e.g., `calculate_metric`).
*   **Cryptic Variables:** In `doStuff`, variables `a` through `j`, `x`, `y`, and `z` provide no semantic meaning. Use descriptive names (e.g., `value`, `shape_type`, `radius`).
*   **Generic Temp Variables:** `temp1`, `temp2`, and `v` should be renamed to reflect their purpose.

**2. Software Engineering Standards**
*   **Modularization:** `doStuff` has too many arguments (10) and handles too many unrelated responsibilities. Split it into smaller, focused functions.
*   **Global State:** The use of `global total_result` makes the code harder to test and thread-unsafe. Pass the state as an argument or use a class.
*   **Mutable Default Arguments:** `collectValues(x, bucket=[])` uses a mutable list as a default. This causes the list to persist across function calls, leading to unexpected behavior. Use `bucket=None` and initialize inside the function.

**3. Logic & Correctness**
*   **Deep Nesting:** The nested `if` blocks in `doStuff` (the "Arrow Anti-pattern") are difficult to read and maintain. Flatten these using guard clauses or a mapping.
*   **Broad Exception Handling:** `except:` in `processEverything` catches all exceptions (including KeyboardInterrupt). Use `except ValueError:`.
*   **Redundant Logic:** `temp1 = z + 1` followed by `temp2 = temp1 - 1` is a no-op that simply returns `z`.
*   **Type Checking:** `type(item) == int` is less flexible than `isinstance(item, int)`.

**4. Performance & Security**
*   **Unnecessary Delay:** `time.sleep(0.01)` inside a loop significantly degrades performance without a clear purpose.
*   **Inefficient Conversion:** `float(str(sum))` is an expensive and unnecessary way to cast a number to a float. Use `float(sum)`.

**5. Readability & Consistency**
*   **Dead Code:** The block `if i or j: pass` does nothing and should be removed.
*   **Magic Numbers:** `3.14159` and `2.71828` should be replaced with `math.pi` and `math.e`.