- Code Smell Type: Security Vulnerability (Arbitrary Code Execution)
- Problem Location: `def unsafe_eval(user_code): return eval(user_code)`
- Detailed Explanation: The use of `eval()` on input that is explicitly named `user_code` allows for arbitrary code execution. An attacker could pass malicious strings to execute system commands, delete files, or steal data, posing a critical security risk.
- Improvement Suggestions: Avoid `eval()` entirely. If the goal is to evaluate mathematical expressions, use a safe library like `ast.literal_eval` or a dedicated expression parser.
- Priority Level: High

- Code Smell Type: Unclear Naming
- Problem Location: `def f(x):`
- Detailed Explanation: The function name `f` is non-descriptive and provides no semantic meaning regarding its purpose or the transformation it performs on `x`. This hinders readability and maintainability.
- Improvement Suggestions: Rename the function to reflect its mathematical or business purpose (e.g., `calculate_offset_value` or `apply_linear_transformation`).
- Priority Level: Medium

- Code Smell Type: Tight Coupling / Hidden Dependency (Global State)
- Problem Location: `def secret_behavior(x):` and `def run_task():` (referencing `hidden_flag` and `global_config`)
- Detailed Explanation: These functions depend on global variables. This makes the code harder to test (requires setup/teardown of global state), prone to side-effect bugs, and difficult to reason about in a multi-threaded or complex environment.
- Improvement Suggestions: Pass the configuration or flags as arguments to the functions (Dependency Injection). For example: `def secret_behavior(x, is_hidden=True):`.
- Priority Level: Medium

- Code Smell Type: Overly Broad Exception Handling
- Problem Location: `def risky_update(data):` inside the `except Exception:` block.
- Detailed Explanation: Catching the base `Exception` class hides all possible errors, including `KeyboardInterrupt`, `MemoryError`, or `TypeError` (e.g., if `data` is not a dictionary). This makes debugging difficult as it masks the root cause of failures.
- Improvement Suggestions: Catch specific exceptions that are expected, such as `KeyError` or `TypeError`.
- Priority Level: Medium

- Code Smell Type: Violation of Single Responsibility Principle (Mixing Logic and I/O)
- Problem Location: `def process_user_input(user_input):`
- Detailed Explanation: The function is responsible for both validating/processing logic and printing output to the console. This makes the function non-reusable in contexts where printing is not desired (e.g., a GUI or an API) and complicates unit testing.
- Improvement Suggestions: Separate the logic from the I/O. The function should return a result or raise an exception, and the caller should handle the printing/logging.
- Priority Level: Low