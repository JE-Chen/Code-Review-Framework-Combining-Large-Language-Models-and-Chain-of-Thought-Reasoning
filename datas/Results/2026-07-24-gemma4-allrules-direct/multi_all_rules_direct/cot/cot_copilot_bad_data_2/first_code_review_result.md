### Code Review

**Logic & Correctness**
* **`unsafe_eval`**: Use of `eval()` on `user_code` is a critical security vulnerability. Avoid dynamic code execution of external input.
* **`risky_update`**: Catching a broad `Exception` can hide unexpected bugs (e.g., `TypeError` if `data` is not a dict). Catch specific exceptions like `KeyError` or `TypeError`.

**Naming Conventions**
* **`f(x)`**: Function name is non-descriptive. Rename to reflect its purpose (e.g., `calculate_offset_value`).

**Software Engineering Standards**
* **`process_user_input`**: This function violates the Single Responsibility Principle by mixing validation, business logic, and I/O (`print` statements). Separate the logic from the output.
* **`secret_behavior`**: Relies on a global `hidden_flag`, making the function's behavior implicit and harder to test. Pass the flag as an explicit parameter.
* **`run_task`**: Relies on a global `global_config` dictionary, creating hidden coupling. Pass the configuration explicitly.

**Readability & Consistency**
* **`check_value`**: Uses implicit truthiness (`if val:`). Use explicit comparisons (e.g., `if val is not None:`) to avoid bugs with empty strings or zeros.
* **`timestamped_message`**: Direct dependency on `time.time()` makes the function non-deterministic and difficult to unit test. Consider passing the timestamp as an argument.

**Performance & Security**
* **`risky_update`**: Modifies the `data` input argument in place. This can cause surprising side effects for the caller; consider returning a new object or documenting the mutation.