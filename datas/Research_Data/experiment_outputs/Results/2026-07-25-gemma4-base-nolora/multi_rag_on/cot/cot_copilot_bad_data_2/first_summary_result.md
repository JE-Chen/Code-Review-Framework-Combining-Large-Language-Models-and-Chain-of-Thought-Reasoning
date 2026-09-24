Based on the provided code and the global/RAG rules, here is the code review.

### 1. Logic & Correctness
*   **`risky_update` function**: The `try...except Exception` block is too broad. Catching all exceptions can hide critical bugs (like `TypeError` if `data` is not a dictionary). It is better to catch specific exceptions (e.g., `KeyError`).

### 2. Performance & Security
*   **`unsafe_eval` function**: **Critical Security Risk.** The use of `eval()` on `user_code` allows for arbitrary code execution. This violates the RAG rule: *"Avoid using eval, exec, or dynamic code execution unless there is a strong justification."* This should be removed or replaced with a safe alternative like `ast.literal_eval()` if only data parsing is needed.

### 3. Software Engineering Standards
*   **`risky_update` function**: This function modifies the `data` input argument directly. This violates the RAG rule: *"Avoid modifying input arguments unless it is clearly documented and expected."* It is recommended to create a copy of the dictionary or return a new object.
*   **`secret_behavior` and `run_task`**: Both functions rely on shared mutable state (`hidden_flag` and `global_config`). This violates the RAG rule regarding shared mutable state at the module level, which introduces hidden coupling and makes testing difficult. These should be passed as arguments to the functions.

### 4. Naming Conventions
*   **`f(x)`**: The function name `f` is not descriptive. According to Rule 2, names must be meaningful. Please rename this to reflect its actual purpose (e.g., `calculate_linear_transformation`).

### 5. Documentation & Testing
*   **`timestamped_message`**: This function makes a direct call to `time.time()`. Per RAG rules, time-dependent logic should be abstracted (e.g., by passing the timestamp as an argument) to ensure tests are deterministic.

---

### Summary of Findings

| Category | Issue | Severity | Rule Violated |
| :--- | :--- | :--- | :--- |
| **Security** | Use of `eval()` in `unsafe_eval` | Critical | RAG: No `eval`/`exec` |
| **Engineering** | Mutation of input `data` in `risky_update` | Medium | RAG: No input mutation |
| **Engineering** | Reliance on `global_config` and `hidden_flag` | Medium | RAG: Shared mutable state |
| **Naming** | Non-descriptive function name `f` | Low | Rule 2: Naming Conventions |
| **Testing** | Direct `time.time()` call | Low | RAG: Time-dependent logic |
| **Logic** | Overly broad `Exception` catch | Low | Rule 4: Exception handling |