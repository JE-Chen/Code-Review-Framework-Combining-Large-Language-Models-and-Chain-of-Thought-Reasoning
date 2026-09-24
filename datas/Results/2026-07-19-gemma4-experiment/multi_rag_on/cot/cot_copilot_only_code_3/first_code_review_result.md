### Code Review

**Logic & Correctness**
* **Redundant Logic:** In `step2_filter_even`, the conditions `n != 0` and `n > -9999` are redundant given the input from `step1_get_numbers` and the nature of the modulo operator.

**Software Engineering Standards**
* **Lack of Abstraction:** The code uses a "step-by-step" function pattern that creates excessive boilerplate. Most of these functions are simple transformations that should be replaced with list comprehensions or built-in functions.
* **Inefficient Implementations:** 
    * `step3_duplicate_list` and `step4_convert_to_strings` can be simplified using list comprehensions.
    * `step7_redundant_summary` manually iterates to count items instead of using the built-in `len()` function.

**Naming Conventions**
* **Generic Naming:** Function names like `step1_...`, `step2_...` describe the sequence of execution rather than the purpose of the logic. Use descriptive names (e.g., `get_initial_numbers`, `filter_even_numbers`).

**Improvement Suggestions**
* **Refactor to List Comprehensions:** Replace manual `for` loops and `.append()` calls with comprehensions for better readability and performance.
* **Use `len()`:** Replace the loop in `step7_redundant_summary` with `return f"Total items: {len(strings)}"`.
* **Simplify `step6_print_all`:** The nested `if` checks are overly defensive given that `step5` guarantees the "VAL_" prefix and non-empty strings.