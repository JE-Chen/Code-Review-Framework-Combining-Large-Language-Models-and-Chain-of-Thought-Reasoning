## PR Summary

*   **Key changes**: Implementation of various utility functions for list manipulation, conditional logic, and basic calculations.
*   **Impact scope**: General utility module.
*   **Purpose of changes**: Initial implementation of helper functions.
*   **Risks and considerations**: Several functions contain patterns that may lead to unexpected state behavior or security vulnerabilities.

---

## Code Review

### 1. Logic & Correctness / RAG Rules

*   **Mutable Default Arguments**: In `add_item(item, container=[])`, the default list is evaluated once at definition. Subsequent calls will share the same list instance.
    *   *Recommendation*: Use `container=None` and initialize inside the function: `if container is None: container = []`.
*   **Shared Mutable State**: `shared_list` is a module-level global variable mutated by `append_global`. This introduces hidden coupling and makes testing difficult.
    *   *Recommendation*: Pass the list as an explicit argument to the function.
*   **Input Mutation**: `mutate_input(data)` modifies the input list in place. This can cause surprising side effects for the caller.
    *   *Recommendation*: Create a new list (e.g., using a list comprehension) and return it, or document the mutation clearly.
*   **Deeply Nested Logic**: `nested_conditions(x)` has three levels of nesting, increasing cognitive load.
    *   *Recommendation*: Use guard clauses (early returns) to flatten the structure.
*   **Inconsistent Return Types**: `inconsistent_return(flag)` returns an `int` in one branch and a `str` in another. This forces the caller to perform type checking.
    *   *Recommendation*: Return a consistent type.
*   **Side Effects in Comprehensions**: `side_effects = [print(i) for i in range(3)]` uses a list comprehension solely for the side effect of printing.
    *   *Recommendation*: Use a standard `for` loop.
*   **Dynamic Code Execution**: `run_code` uses `eval()`, which is a significant security risk if `code_str` comes from an untrusted source.
    *   *Recommendation*: Avoid `eval` unless absolutely necessary; use safer alternatives like `ast.literal_eval` or a predefined mapping.

### 2. Performance & Security

*   **Loop Invariants**: In `compute_in_loop(values)`, `len(values)` is called in every iteration. While `len()` is $O(1)$ in Python, it is still a repeated operation.
    *   *Recommendation*: Assign `limit = len(values)` outside the loop.
*   **Broad Exception Handling**: `risky_division` catches `Exception`. This is too broad and could hide bugs (e.g., `KeyboardInterrupt` or `TypeError`).
    *   *Recommendation*: Catch only `ZeroDivisionError`.

### 3. Software Engineering Standards

*   **Magic Numbers**: `calculate_area` uses `3.14159` as a hard-coded constant.
    *   *Recommendation*: Use `math.pi` for better precision and readability.
*   **Single Responsibility**: `nested_conditions` is handling too many categories of logic in one block.
    *   *Recommendation*: Split into smaller helper functions (e.g., `_classify_positive`).

### 4. Readability & Consistency

*   **Implicit Truthiness**: While not explicitly failing here, the codebase should ensure explicit comparisons (e.g., `if flag is True:`) when dealing with complex objects to avoid ambiguity.