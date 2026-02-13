### Code Review Feedback

- **Naming Conventions**  
  - `doStuff` is vague and uninformative. Rename to something descriptive like `calculate_shape_value`.  
  - Parameters (e.g., `a`, `b`, `c`) lack semantic meaning. Replace with clear names like `input_value`, `shape_type`, `radius`.  
  - `total_result` (global) is ambiguous. Avoid globals; return values instead.

- **Function Design & Responsibility**  
  - `doStuff` handles math, conditionals, global mutation, and sleeps. Split into focused functions (e.g., `compute_shape_value`, `apply_math_operations`).  
  - `collectValues` uses a mutable default list (`bucket=[]`). This causes unexpected behavior (e.g., shared state across calls). Initialize `bucket` as `None` and assign `[]` inside the function.

- **Logic & Redundancy**  
  - `temp1` and `temp2` in `doStuff` cancel each other out. Replace with `result = z` to simplify logic.  
  - The `if i or j` check in `doStuff` is dead code (always `False` since `i`/`j` are `None`). Remove it.  
  - The `else` branch for `b` in `doStuff` is never used (caller only passes `"square"`/`"circle"`). Remove it to reduce complexity.

- **Performance & Side Effects**  
  - `time.sleep(0.01)` adds artificial delay. Remove unless required for specific testing.  
  - Global variable `total_result` complicates state management and testing. Eliminate by returning values.

- **Other Issues**  
  - `processEverything` shadows built-in `sum` with `sum = total`. Rename to avoid conflicts.  
  - `processEverything` converts inputs to integers but ignores fractional parts (e.g., `4.5` → `4`). Clarify intent or handle floats explicitly.  
  - No docstrings or inline comments. Add minimal explanations for non-obvious logic.

- **Critical Flaw**  
  - `collectValues` default argument bug:  
    ```python
    # ❌ Bad (shared state across calls)
    def collectValues(x, bucket=[]):
        bucket.append(x)
        return bucket
    
    # ✅ Fix (initialize inside function)
    def collectValues(x, bucket=None):
        if bucket is None:
            bucket = []
        bucket.append(x)
        return bucket
    ```

- **Improvement Summary**  
  Refactor `doStuff` to eliminate globals, reduce parameters, and simplify logic. Remove dead code and redundant operations. Replace `collectValues` default argument. Use descriptive names throughout. These changes will improve readability, testability, and maintainability.