Here is the code review based on the provided global rules.

### 1. Readability & Consistency
- **Formatting:** The code is generally well-formatted, but there is a strange use of a list literal `[results.append(cache[item])]` on line 14. This is non-standard and confusing; it should be a simple function call.

### 2. Naming Conventions
- **Naming:** Variable and function names (`process_items`, `expensive_compute`, `get_user_data`) are descriptive and follow standard Python naming conventions.

### 3. Software Engineering Standards
- **Mutable Default Arguments:** In `process_items(items=[], ...)` (line 7), using a list as a default argument is a dangerous Python anti-pattern. The list is created once at definition time and shared across all calls, leading to unexpected behavior if the list is modified.
- **Global State:** The use of global variables `cache` and `results` makes the code difficult to test and not thread-safe. `results` in particular accumulates data across every call to `process_items`, which is likely a bug.

### 4. Logic & Correctness
- **Accumulation Bug:** Because `results` is a global list, every call to `process_items` appends to the same list. In `main()`, `output2` will contain the results of both the first and second calls.
- **Logic Error:** In `expensive_compute`, the check `if x == 0: return None` is followed by `if x < 0: return "invalid"`. While logically sound, the `eval` block is redundant for simple multiplication.

### 5. Performance & Security
- **Critical Security Risk:** The use of `eval(f"{x} * {x}")` in `expensive_compute` (line 26) is a severe security vulnerability. If `x` is passed as a string from an untrusted source (e.g., via `get_user_data`), it allows for **Arbitrary Code Execution**.
- **Performance:** `time.sleep(0.01)` inside a loop (line 12) introduces an artificial bottleneck that should be removed unless specifically required for rate-limiting.

### 6. Documentation & Testing
- **Missing Documentation:** There are no docstrings explaining the purpose of the functions or the expected types of the arguments.
- **Testing:** No unit tests are provided to verify the edge cases (0, negative numbers, or invalid inputs).

---

### Summary of Major Issues
| Category | Issue | Severity |
| :--- | :--- | :--- |
| **Security** | `eval()` usage allows remote code execution. | **Critical** |
| **Logic** | Global `results` list causes data leakage between calls. | **High** |
| **Engineering** | Mutable default argument `items=[]`. | **Medium** |
| **Readability** | Unnecessary list wrapper around `results.append()`. | **Low** |