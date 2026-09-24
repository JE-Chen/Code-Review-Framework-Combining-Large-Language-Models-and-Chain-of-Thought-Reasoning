This code review is conducted based on the provided global rules.

### 1. Readability & Consistency
- **Formatting:** The code generally follows PEP 8 indentation, but the logic flow is hindered by excessive nesting.
- **Consistency:** The use of `type(item) == int` is inconsistent with Pythonic type checking (should use `isinstance`).

### 2. Naming Conventions
- **Non-Descriptive Names:** The function `doStuff` and variables `a, b, c, d, e, f, g, h, i, j, x, y, z` are completely devoid of semantic meaning. This makes the code nearly impossible to maintain or audit without reverse-engineering the logic.
- **Generic Names:** `processEverything` and `collectValues` are too generic.
- **Shadowing:** The variable `sum` in `processEverything` shadows the built-in Python `sum()` function.

### 3. Software Engineering Standards
- **Modularization:** `doStuff` is a "God Function" attempting to handle too many unrelated logical branches. It should be split into smaller, single-responsibility functions (e.g., one for geometry calculations, one for arithmetic operations).
- **Complexity:** The nested `if` statements in `doStuff` create a "pyramid of doom," significantly increasing cognitive load and making testing difficult.
- **Abstraction:** The logic for converting `item` to an integer in `processEverything` is repetitive and should be abstracted into a helper function.

### 4. Logic & Correctness
- **Exception Handling:** The `try...except:` block in `processEverything` is a "bare except," which catches all exceptions (including `KeyboardInterrupt`), which is a dangerous practice.
- **Redundant Logic:** 
    - `temp1 = z + 1` followed by `temp2 = temp1 - 1` is a no-op; it simply returns `z`.
    - `if i or j: pass` does nothing and should be removed.
- **Type Conversion:** `final_result = float(str(sum))` is an inefficient and illogical way to cast a number to a float. Use `float(sum)`.

### 5. Performance & Security
- **Artificial Latency:** `time.sleep(0.01)` inside a loop in `doStuff` introduces a significant performance bottleneck for no apparent reason.
- **Global State:** The use of `global total_result` makes the code thread-unsafe and difficult to test in isolation.
- **Mutable Default Arguments:** In `collectValues(x, bucket=[])`, the list `bucket` is shared across all calls to the function. This is a classic Python bug where subsequent calls will contain values from previous calls.

### 6. Documentation & Testing
- **Missing Documentation:** There are no docstrings or comments explaining the purpose of the calculations or the expected input/output formats.
- **Testing:** No unit tests are provided for the complex branching logic in `doStuff`.

---

### Summary of Major Issues
| Category | Issue | Severity |
| :--- | :--- | :--- |
| **Naming** | Meaningless variable names (`a` through `j`) | High |
| **Logic** | Mutable default argument in `collectValues` | High |
| **Performance** | Unnecessary `time.sleep` and `global` state | Medium |
| **Clean Code** | Deeply nested conditionals and redundant math | Medium |
| **Correctness** | Bare `except` block | Medium |