### Code Review

**Logic & Security**
* **Critical Security Risk:** `unsafe_eval` uses `eval()`, which allows arbitrary code execution. This is a severe security vulnerability. Use a safe alternative like `ast.literal_eval` or a dedicated parser.
* **Input Mutation:** `risky_update` modifies the `data` dictionary in place. Per RAG rules, avoid modifying input arguments to prevent unexpected side effects for the caller.

**Naming Conventions**
* **Vague Naming:** Function `f(x)` is non-descriptive. Rename it to reflect its mathematical purpose (e.g., `calculate_linear_offset`).

**Software Engineering Standards**
* **Shared Mutable State:** `hidden_flag` and `global_config` are defined at the module level and used inside functions. This creates hidden coupling; prefer passing these as arguments to improve testability and predictability.
* **Environment Dependency:** `timestamped_message` calls `time.time()` directly. This makes the function non-deterministic and difficult to unit test. Inject the time or a clock provider as a dependency.

**Readability & Consistency**
* **Redundant Logic:** In `process_user_input`, the `else` block is unnecessary after a `return` statement. Use a guard clause to flatten the logic.
* **Generic Exception Handling:** `risky_update` uses a bare `except Exception:`, which can hide unexpected bugs (e.g., `KeyboardInterrupt` or `MemoryError`). Catch specific exceptions (e.g., `KeyError`, `TypeError`).