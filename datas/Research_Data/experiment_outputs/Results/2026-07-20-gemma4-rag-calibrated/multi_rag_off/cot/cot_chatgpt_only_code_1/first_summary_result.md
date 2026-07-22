Here is the code review based on the provided global rules.

### 1. Readability & Consistency
- **Formatting:** The code generally follows PEP 8 indentation, but the logic flow is hindered by excessive nesting.
- **Redundancy:** In `doStuff`, the lines `temp1 = z + 1`, `temp2 = temp1 - 1`, and `result = temp2` are mathematically redundant and should be simplified to `result = z`.

### 2. Naming Conventions
- **Non-Descriptive Names:** Function names like `doStuff` and `processEverything` are generic and do not describe the business logic.
- **Variable Names:** Variables `a` through `j` in `doStuff` and `flag1` through `flag5` in `processEverything` lack semantic meaning, making the logic difficult to follow and maintain.
- **Shadowing:** The variable name `sum` in `processEverything` shadows the built-in Python `sum()` function.

### 3. Software Engineering Standards
- **Modularization:** `doStuff` is overloaded with too many responsibilities (calculation, global state modification, and artificial delays). It should be split into smaller, pure functions.
- **Global State:** The use of `global total_result` makes the code harder to test and thread-unsafe. State should be passed explicitly or managed via a class.
- **Abstraction:** The type-checking logic in `processEverything` (converting various types to `int`) should be extracted into a helper function (e.g., `to_int()`).

### 4. Logic & Correctness
- **Deep Nesting:** The nested `if` statements in `doStuff` (up to 5 levels) are a "pyramid of doom" and are highly prone to logic errors.
- **Exception Handling:** The `except:` block in `processEverything` is a "bare except," which catches all exceptions including `KeyboardInterrupt` and `SystemExit`. It should be `except ValueError:`.
- **Type Checking:** Using `type(item) == int` is less flexible than `isinstance(item, int)`.

### 5. Performance & Security
- **Artificial Bottleneck:** `time.sleep(0.01)` inside a loop in `doStuff` introduces a significant performance penalty without a clear purpose.
- **Complexity:** The conversion `float(str(sum))` is inefficient; `float(sum)` is sufficient.

### 6. Documentation & Testing
- **Missing Documentation:** There are no docstrings or comments explaining the purpose of the calculations or the expected input/output formats.
- **Testing:** No unit tests are provided to verify the complex conditional logic in `doStuff`.

### 7. Critical Bug: Mutable Default Arguments
- **Bug in `collectValues`:** The function uses a mutable default argument `bucket=[]`. In Python, default arguments are evaluated once at definition time. Subsequent calls to `collectValues` will append to the *same* list across different calls, leading to unexpected behavior (as seen in the `__main__` output where the list grows cumulatively).
- **Fix:** Use `bucket=None` and initialize inside the function: `if bucket is None: bucket = []`.

---

### Summary of Recommendations
1. **Refactor `doStuff`**: Replace the nested `if` blocks with a flatter structure or a lookup table.
2. **Rename Variables**: Use descriptive names (e.g., `value`, `shape_type`, `is_enabled`).
3. **Fix Mutable Default**: Change `bucket=[]` to `bucket=None`.
4. **Remove Global State**: Pass `total_result` as a return value or use a class.
5. **Clean up Types**: Use `isinstance()` and specific exception handling (`ValueError`).