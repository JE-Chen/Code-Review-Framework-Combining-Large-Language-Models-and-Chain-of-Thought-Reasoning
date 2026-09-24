### Code Review

**Logic & Security**
* **Critical Security Risk:** `unsafe_eval` uses `eval()`, which allows arbitrary code execution. This is a severe security vulnerability. Remove it or use a safe alternative like `ast.literal_eval`.
* **Input Mutation:** `risky_update` modifies the `data` dictionary in place. Per RAG rules, avoid modifying input arguments to prevent unexpected side effects for the caller.

**Naming Conventions**
* **Vague Naming:** The function `f(x)` is cryptically named. Rename it to describe its purpose (e.g., `calculate_offset_value`).

**Software Engineering Standards**
* **Shared Mutable State:** `hidden_flag` and `global_config` are defined at the module level and used inside functions. This introduces hidden coupling; prefer passing these as arguments to improve testability and predictability.
* **Environment Dependency:** `timestamped_message` calls `time.time()` directly. This makes the function non-deterministic and difficult to unit test. Pass the timestamp as an argument instead.

**Readability & Maintainability**
* **Hard-coded Constants:** The values `7` and `13` in `f(x)` are "magic numbers." Move these to named constants at the top of the file.
* **Exception Handling:** `risky_update` uses a bare `except Exception:`, which can catch and hide unexpected errors (like `KeyboardInterrupt` or `MemoryError`). Catch specific exceptions (e.g., `KeyError`, `TypeError`).