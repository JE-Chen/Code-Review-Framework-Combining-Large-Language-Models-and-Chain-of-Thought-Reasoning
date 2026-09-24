### Code Review

**Logic & Correctness / RAG Rules**
*   **Mutable Default Argument:** In `add_item`, `container=[]` is evaluated once at definition. Subsequent calls will share the same list across different invocations. Use `container=None` and initialize inside the function.
*   **Shared Mutable State:** `shared_list` is a global variable mutated by `append_global`. This introduces hidden coupling and makes testing difficult.
*   **Input Mutation:** `mutate_input` modifies the `data` list in place. This can cause unexpected side effects for the caller.
*   **Deep Nesting:** `nested_conditions` has excessive nesting. Use guard clauses (early returns) to flatten the logic and reduce cognitive load.
*   **Broad Exception Handling:** `risky_division` catches `Exception`. This can hide unexpected errors (e.g., `TypeError`). Catch `ZeroDivisionError` specifically.
*   **Inconsistent Return Types:** `inconsistent_return` returns both an `int` and a `str`. This forces callers to perform type checking and increases runtime error risks.
*   **Inefficient Loop Logic:** In `compute_in_loop`, `len(values)` is recalculated in every iteration. Move this invariant calculation outside the loop.
*   **Side Effects in Comprehension:** `side_effects` uses a list comprehension to call `print()`. Comprehensions should be used for building collections, not for executing logic. Use a standard `for` loop.
*   **Security Risk:** `run_code` uses `eval()`, which allows execution of arbitrary code and poses a severe security vulnerability.
*   **Magic Numbers:** `calculate_area` uses a hard-coded value for Pi. Use `math.pi` for better precision and clarity.

**Naming & Readability**
*   **Naming:** Function names like `nested_conditions` and `inconsistent_return` describe the *implementation flaw* rather than the *business purpose*. Use descriptive names reflecting the intent of the logic.