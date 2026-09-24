### Code Review

**Naming Conventions**
* **Function Naming:** The `stepX_` prefix (e.g., `step1_get_numbers`) describes the sequence of execution rather than the purpose of the function. Rename these to reflect their actual responsibility (e.g., `get_numbers`, `filter_even_numbers`).

**Logic & Correctness**
* **Redundant Logic:** In `step2_filter_even`, the conditions `n != 0` and `n > -9999` are redundant given the input from `step1_get_numbers` and the nature of the modulo operator for the intended goal.
* **Implicit Truthiness:** In `step6_print_all`, `if len(s) > 0:` should be replaced with an explicit comparison or a more Pythonic check, though the current logic is functional.

**Software Engineering Standards**
* **Modularity & Efficiency:** Several functions (`step3`, `step4`, `step5`) use manual loop-and-append patterns that are better handled by list comprehensions for readability and performance.
* **Redundant Implementation:** `step7_redundant_summary` manually iterates to count items; use the built-in `len()` function instead.

**Improvement Suggestions**
* **Refactor Loops:** Use list comprehensions for transformations.
  * *Example:* `return [str(n) for n in nums]` instead of the loop in `step4`.
* **Simplify Summary:** Replace the loop in `step7` with `return f"Total items: {len(strings)}"`.
* **Clean up Conditionals:** Use guard clauses in `step6_print_all` to reduce nesting levels.