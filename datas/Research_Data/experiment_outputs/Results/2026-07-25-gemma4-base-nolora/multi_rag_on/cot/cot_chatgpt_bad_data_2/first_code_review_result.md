### Code Review

**Logic & Correctness**
*   **Mutable Default Argument:** In `process(service, data=[], ...)`: The list `data=[]` is shared across all function calls. This will cause data to accumulate across multiple calls to `process`, leading to unexpected behavior. Use `data=None` and initialize inside the function.
*   **Resource Leak:** In `_load_from_file`, the file is opened using `f = open(path)`. If an exception occurs before `f.close()`, the file handle remains open. Use a `with open(path) as f:` block.
*   **Silent Failure:** The `except Exception: pass` block in `_load_from_file` swallows all errors (e.g., `FileNotFoundError`), making debugging impossible. At minimum, log the error.
*   **Uninitialized Variable:** In `main()`, if `CONFIG["retry"]` is 0 or less, the variable `result` is never defined, causing a `UnboundLocalError` when `print("Results:", result)` is called.

**Software Engineering Standards**
*   **Class State Management:** `users = {}` is defined as a class attribute, not an instance attribute. This means all instances of `UserService` share the same user list, which is likely unintended. Move it to `__init__` as `self.users = {}`.

**Readability & Naming**
*   **Naming:** The function name `process` is too generic. A more descriptive name like `collect_user_keys` or `sync_user_data` would improve clarity.

**Performance**
*   **Unnecessary Delay:** `time.sleep(0.05)` inside `_load_random_users` introduces an artificial bottleneck that serves no apparent purpose in the logic.