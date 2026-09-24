### Code Review

**Logic & Correctness / RAG Violations**
*   **Mutable Default Argument:** In `add_item`, `container=[]` is evaluated once at definition. Subsequent calls will share the same list across different invocations. Use `container=None` and initialize inside the function.
*   **Shared Mutable State:** `shared_list` is a global variable mutated by `append_global`, creating hidden coupling and making the code harder to test.
*   **Input Mutation:** `mutate_input` modifies the `data` list in place. This is a side effect that can surprise callers; return a new list instead.
*   **Deeply Nested Logic:** `nested_conditions` has excessive nesting. Use guard clauses (early returns) to flatten the structure and reduce cognitive load.
*   **Inconsistent Return Types:** `inconsistent_return` returns an `int` in one branch and a `str` in another, which forces the caller to perform type checking.
*   **Side Effects in Comprehension:** `side_effects = [print(i) for i in range(3)]` uses a list comprehension for its side effect (`print`). Use a standard `for` loop.
*   **Security Risk:** `run_code` uses `eval()`, which allows execution of arbitrary code and poses a severe security vulnerability.
*   **Broad Exception Handling:** `risky_division` catches `Exception`. Be specific (e.g., `ZeroDivisionError`) to avoid silencing unrelated system errors.

**Performance & Engineering Standards**
*   **Invariant in Loop:** In `compute_in_loop`, `len(values)` is recalculated in every iteration. Move this to a variable outside the loop.
*   **Magic Numbers:** `calculate_area` uses `3.14159`. Use `math.pi` for better precision and readability.

**Naming & Readability**
*   The naming is generally descriptive, but the overall structure lacks modularity due to the mix of global state and utility functions.