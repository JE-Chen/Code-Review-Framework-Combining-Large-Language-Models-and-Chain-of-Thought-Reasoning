### Code Review

**1. Readability & Consistency**
* **Resource Management:** In `_load_from_file`, the file is opened and closed manually. Use a `with open(path) as f:` block to ensure the file is closed even if an exception occurs.

**2. Naming Conventions**
* **Variable Naming:** In `process()`, the variable `key` is used to iterate over `service.users`. Since it represents a username, `username` or `user_id` would be more descriptive.

**3. Software Engineering Standards**
* **Mutable Default Arguments:** The `process` function uses `data=[]` as a default argument. In Python, default lists are shared across all calls to the function, which will lead to unexpected data accumulation. Use `data=None` and initialize inside the function.
* **Class State:** `users = {}` is defined as a class attribute, meaning it is shared across all instances of `UserService`. If this is intended to be instance-specific, move it into `__init__`.

**4. Logic & Correctness**
* **Silent Failures:** The `try...except Exception: pass` block in `_load_from_file` swallows all errors. This makes debugging impossible if the file is missing or permissions are denied. Log the error or raise a specific exception.
* **Return Type Inconsistency:** The `process` function returns a `list` on success but `False` (a boolean) if no data is found. It is better to return an empty list `[]` to maintain a consistent return type.
* **Uninitialized Variable:** In `main()`, the variable `result` is defined inside an `if` block. If `CONFIG["retry"]` is 0 or less, `print("Results:", result)` will raise an `UnboundLocalError`.

**5. Performance & Security**
* **Input Validation:** `_load_from_file` takes a path but does not validate if the path is safe or exists before attempting to open it.