### Pull Request Summary

*   **Key changes**: Implementation of user input processing, a conditional behavior function, value checking, and a task runner based on global configuration.
*   **Impact scope**: Core utility functions and input handling logic.
*   **Purpose of changes**: Initial implementation of basic business logic and system utilities.
*   **Risks and considerations**: Presence of security vulnerabilities (`eval`) and unpredictable behavior due to global state and broad exception handling.

---

### Code Review

#### 1. Logic & Correctness
*   **`risky_update`**: The function catches `Exception` (broad exception), which can hide unexpected errors (e.g., `TypeError` if `data` is not a dictionary). It should catch specific exceptions like `KeyError` or `TypeError`.

#### 2. Naming Conventions
*   **`f(x)`**: The function name `f` is non-descriptive. It should be renamed to reflect its mathematical purpose (e.g., `calculate_linear_transform`).

#### 3. Software Engineering Standards
*   **`process_user_input`**: This function violates the **Single Responsibility Principle**. It performs validation, business logic (access check), and I/O (printing) simultaneously. It should be split into a validation/logic function and a separate handler for output.
*   **`secret_behavior`**: This function relies on a `hidden_flag` (global state), making its behavior implicit and difficult to test. The flag should be passed as an explicit parameter.
*   **`run_task`**: Relies on `global_config` (shared mutable state), which introduces hidden coupling.

#### 4. Performance & Security
*   **`unsafe_eval`**: **Critical Security Risk.** The use of `eval()` on `user_code` allows for arbitrary code execution. This should be removed or replaced with a safe alternative (e.g., `ast.literal_eval` if only data structures are expected).

#### 5. RAG Rules Compliance
*   **Implicit Truthiness**: In `check_value(val)`, the check `if val:` relies on implicit truthiness. This can lead to bugs if `val` is `0` or an empty string when those should be treated as "having a value." Use explicit comparisons (e.g., `if val is not None:`).
*   **Modifying Input Arguments**: `risky_update` modifies the `data` dictionary in place. This can cause side effects for the caller. It is safer to return a new dictionary or document the mutation clearly.
*   **Environment-Dependent Logic**: `timestamped_message` calls `time.time()` directly. This makes the function non-deterministic and hard to unit test. The timestamp should be passed as an argument or provided via a clock abstraction.

#### 6. Documentation & Testing
*   The codebase lacks docstrings and type hints, making the expected types for `user_input`, `x`, and `data` ambiguous.