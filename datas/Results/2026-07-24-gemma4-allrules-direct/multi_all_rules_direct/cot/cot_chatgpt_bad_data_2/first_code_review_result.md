### Code Review

**1. Logic & Correctness**
*   **Broad Exception Handling:** In `_load_from_file`, `except Exception: pass` silences all errors (e.g., `FileNotFoundError`), making debugging impossible. Catch specific exceptions.
*   **Resource Management:** `_load_from_file` opens a file without a `with` statement. If an exception occurs before `f.close()`, the file handle remains open.
*   **Inconsistent Return Types:** The `process` function returns a `list` on success and `False` (boolean) on failure. This forces callers to use type-checking or implicit truthiness, which is error-prone.

**2. RAG Rule Violations**
*   **Mutable Default Arguments:** `process(service, data=[])` uses a list as a default argument. This list is shared across all calls to `process`, leading to unexpected data accumulation. Use `data=None`.
*   **Shared Mutable State:** `UserService.users = {}` is defined as a class attribute. All instances of `UserService` will share the same user dictionary, creating hidden coupling. Move this to `__init__`.
*   **Implicit Truthiness:** `if data:` in `process` relies on implicit truthiness. Use explicit checks (e.g., `if len(data) > 0:`) for clarity.

**3. Software Engineering Standards**
*   **Single Responsibility:** `_load_from_file` and `_load_random_users` both handle data retrieval and state mutation (`self.users[name] = ...`). Separate the loading logic from the state update.
*   **Hard-coded Constants:** The filename `"users.txt"` and the range `10` in `_load_random_users` are magic values. Move them to the `CONFIG` dictionary or class constants.

**4. Readability & Naming**
*   **Variable Naming:** In `main()`, the variable `result` is referenced in a `print` statement but is only defined inside an `if` block. If `CONFIG["retry"] <= 0`, the program will crash with a `UnboundLocalError`.

**Suggested Improvements:**
*   Use `with open(path) as f:` for file operations.
*   Change `data=[]` to `data=None` and initialize inside the function.
*   Move `users = {}` into `UserService.__init__`.
*   Replace `except Exception: pass` with specific error handling and logging.
*   Ensure `result` is initialized in `main()` before the conditional block.