Here is the code review based on the provided global rules.

### 1. Readability & Consistency
- **Resource Management**: In `_load_from_file`, the file is opened and closed manually. It is standard Python practice to use a `with open(path) as f:` block to ensure the file is closed even if an exception occurs.

### 2. Naming Conventions
- **Variable Naming**: In `_load_from_file`, the variable `f` is too generic. `file_handle` or `user_file` would be more descriptive.

### 3. Software Engineering Standards
- **Class State**: `users = {}` is defined as a class attribute, not an instance attribute. This means all instances of `UserService` will share the same user dictionary, which is likely a bug if multiple services are instantiated. It should be initialized inside `__init__` as `self.users = {}`.
- **Modularization**: The `process` function is decoupled from the class, which is good, but it relies on a mutable default argument (see Logic & Correctness).

### 4. Logic & Correctness
- **Mutable Default Argument**: The `process` function defines `data=[]` in its signature. In Python, default lists are created once at definition time and shared across all calls. If `process` is called multiple times, `data` will accumulate values from previous calls. Use `data=None` and initialize inside the function.
- **Silent Failures**: The `try...except Exception: pass` block in `_load_from_file` swallows all errors (including `FileNotFoundError` or `PermissionError`) without logging or notifying the caller. This makes debugging extremely difficult.
- **Return Type Inconsistency**: The `process` function returns a `list` on success but a `bool` (`False`) if no data is found. This forces the caller to handle mixed types. It is better to return an empty list `[]`.
- **Unused Variables**: The `result` variable in `main()` is defined inside an `if` block. If `CONFIG["retry"]` were $\le 0$, the `print("Results:", result)` line would raise an `UnboundLocalError`.

### 5. Performance & Security
- **Input Validation**: `_load_from_file` takes a path but does not validate if the path is safe or exists before attempting to open it.
- **Complexity**: The `_load_random_users` method contains a `time.sleep(0.05)` call inside a loop. Unless this is specifically simulating network latency for a test, it is an unnecessary performance bottleneck.

### 6. Documentation & Testing
- **Missing Docstrings**: None of the classes or functions have docstrings explaining their purpose, arguments, or return values.
- **Testing**: No unit tests are provided for the logic, particularly for the `force=True` flag or the different loading sources.

---

### Summary of Recommendations
| Priority | Issue | Recommendation |
| :--- | :--- | :--- |
| **High** | Mutable default argument in `process` | Change `data=[]` to `data=None`. |
| **High** | Class attribute `users` | Move `users = {}` into `__init__`. |
| **Medium** | Silent exception handling | Replace `pass` with logging or specific exception handling. |
| **Medium** | Resource management | Use `with open(...)` context manager. |
| **Low** | Return type inconsistency | Return `[]` instead of `False` in `process`. |