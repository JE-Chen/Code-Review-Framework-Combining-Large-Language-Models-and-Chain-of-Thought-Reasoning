### Code Review

**Logic & Correctness**
* **Mutable Default Argument:** In `process(service, data=[], ...)`: The list `data` is shared across all calls to the function. This will cause data to accumulate across different executions. Use `data=None` and initialize inside the function.
* **Resource Leak:** In `_load_from_file`, the file is opened using `f = open(path)`. If an exception occurs before `f.close()`, the file handle remains open. Use a `with open(path) as f:` block.
* **Silent Failure:** The `try...except Exception: pass` block in `_load_from_file` swallows all errors, making debugging impossible if the file is missing or corrupted.
* **Uninitialized Variable:** In `main()`, if `CONFIG["retry"]` is 0 or less, the variable `result` is never defined, causing a `UnboundLocalError` when printing.

**Software Engineering Standards**
* **Class State Management:** `users = {}` is defined as a class attribute, meaning all instances of `UserService` share the same user dictionary. This should be moved to `__init__` as `self.users = {}` to ensure instance isolation.
* **Return Type Consistency:** The `process` function returns a `list` on success but `False` (a boolean) on failure. It is better to return an empty list `[]` to maintain type consistency.

**Readability & Naming**
* **Naming:** `process` is too generic. A name like `extract_user_list` or `sync_user_data` would be more descriptive.

**Performance & Security**
* **Inefficient String Concatenation:** In `_load_random_users`, use f-strings (e.g., `f"user_{random.randint(1, 100)}"`) for better readability and performance.