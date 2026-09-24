### Code Review

#### 1. Readability & Consistency
- **Formatting:** The code is consistently indented and follows a clear linear flow.
- **Style:** The use of `stepX_` prefixes for function names is unconventional and creates a rigid structure that makes refactoring difficult.

#### 2. Naming Conventions
- **Function Names:** Names like `step1_get_numbers` and `step7_redundant_summary` are descriptive of the *sequence* but not the *intent*. It is better to name functions based on their action (e.g., `get_numbers`, `calculate_summary`).

#### 3. Software Engineering Standards
- **Modularity & Abstraction:** The code is overly fragmented. Each function performs a very simple operation that could be handled more efficiently.
- **Duplicate Logic/Boilerplate:** There is a repetitive pattern of initializing an empty list, looping, and appending. This is a prime candidate for **list comprehensions**, which are more idiomatic in Python.
- **Example Refactor:**
  - `step4_convert_to_strings` and `step5_add_prefix` could be combined or written as:
    `prefixed = [f"VAL_{n}" for n in nums]`

#### 4. Logic & Correctness
- **Redundant Logic:** In `step2_filter_even`, the condition `n != 0` is redundant because `0 % 2 == 0` is true, but the logic specifically excludes zero. If the intent is to exclude zero, it is correct, but the `n > -9999` check is arbitrary and lacks context.
- **Redundant Logic:** In `step6_print_all`, the check `if len(s) > 0` and `if s.startswith("VAL")` is redundant because `step5_add_prefix` guarantees every string starts with `"VAL_"`.
- **Inefficiency:** `step7_redundant_summary` manually iterates to count items. This should be replaced with the built-in `len()` function.

#### 5. Performance & Security
- **Performance:** For the current small dataset, there is no issue. However, the current approach creates six intermediate lists in memory. For larger datasets, using **generators** or combining transformations would significantly reduce memory overhead.

#### 6. Documentation & Testing
- **Documentation:** There are no docstrings or comments explaining the purpose of the transformations or the reason for the specific filters in `step2`.
- **Testing:** No unit tests are provided to verify the filtering or duplication logic.

---

### Summary of Recommendations
1. **Refactor to List Comprehensions:** Replace manual `for` loops and `.append()` calls to improve conciseness and performance.
2. **Remove Redundant Checks:** Simplify `step6` and `step7` by removing checks for conditions that are guaranteed by previous steps and using `len()`.
3. **Rename Functions:** Remove the `stepX_` prefix in favor of semantic names.
4. **Consolidate Logic:** Merge trivial transformation steps to reduce the number of intermediate lists.