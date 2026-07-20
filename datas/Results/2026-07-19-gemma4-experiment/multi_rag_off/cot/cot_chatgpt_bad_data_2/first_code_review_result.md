### Code Review

**Logic & Correctness**
* **Mutable Default Argument:** In `process(service, data=[], ...)`: The list `data=[]` is shared across all calls to the function. This will cause data to accumulate across different executions. Use `data=None` and initialize inside the function.
* **Resource Leak:** In `_load_from_file`, the file is opened manually. If an exception occurs before `f.close()`, the file handle remains open. Use a `with open(path) as f:` block.
* **Silent Failure:** The `try...except Exception: pass` block in `_load_from_file` swallows all errors, making debugging impossible if the file is missing or corrupted.
* **Uninitialized Variable:** In `main()`, if `CONFIG["retry"]` is 0 or less, the variable `result` is never defined, causing a `UnboundLocalError` when printing.

**Software Engineering Standards**
* **Class State Management:** `users = {}` is defined as a class attribute, meaning it is shared across all instances of `UserService`. It should be initialized inside `__init__` as `self.users = {}` to ensure instance isolation.

**Naming & Readability**
* **Vague Naming:** In `process()`, the variable `key` is used to iterate over users; `user_id` or `username` would be more descriptive.

**Performance & Security**
* **Inefficient String Concatenation:** In `_load_random_users`, use f-strings (e.g., `f"user_{random.randint(1, 100)}"`) for better readability and performance.