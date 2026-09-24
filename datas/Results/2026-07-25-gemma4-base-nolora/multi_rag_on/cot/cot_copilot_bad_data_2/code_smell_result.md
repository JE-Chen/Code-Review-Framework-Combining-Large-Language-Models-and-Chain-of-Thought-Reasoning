- Code Smell Type: Security Risk (Dynamic Code Execution)
- Problem Location: `def unsafe_eval(user_code): return eval(user_code)`
- Detailed Explanation: The use of `eval()` on input that is named `user_code` allows for arbitrary code execution. This is a critical security vulnerability that could allow an attacker to execute malicious commands on the host system.
- Improvement Suggestions: Remove `eval()` entirely. If the goal is to evaluate mathematical expressions, use a safe library like `ast.literal_eval` or a dedicated expression parser.
- Priority Level: High

- Code Smell Type: Shared Mutable State
- Problem Location: `hidden_flag = True` and `global_config = {"mode": "debug"}`
- Detailed Explanation: The functions `secret_behavior` and `run_task` depend on global variables. This creates hidden coupling, makes the code harder to test (as tests can interfere with each other), and can lead to unpredictable behavior in multi-threaded environments.
- Improvement Suggestions: Pass these configurations as arguments to the functions (Dependency Injection) or encapsulate them within a configuration class.
- Priority Level: Medium

- Code Smell Type: Unclear Naming
- Problem Location: `def f(x):`
- Detailed Explanation: The function name `f` is non-descriptive and provides no semantic meaning regarding its purpose. This forces the maintainer to read the implementation to understand what the function does, reducing readability.
- Improvement Suggestions: Rename the function to reflect its mathematical purpose or business logic (e.g., `calculate_offset_value`).
- Priority Level: Low

- Code Smell Type: Modifying Input Arguments
- Problem Location: `def risky_update(data):`
- Detailed Explanation: The function modifies the `data` dictionary in place. Mutating input arguments can lead to surprising side effects for the caller, as the original object is changed unexpectedly.
- Improvement Suggestions: Create a copy of the dictionary inside the function, modify the copy, and return it, or clearly document that the function performs an in-place mutation.
- Priority Level: Low

- Code Smell Type: Environment-Dependent Logic (Non-Deterministic)
- Problem Location: `def timestamped_message(msg): return f"{time.time()} - {msg}"`
- Detailed Explanation: Direct calls to `time.time()` make the function non-deterministic, which makes unit testing difficult because the output changes every millisecond.
- Improvement Suggestions: Pass the timestamp as an optional argument to the function, allowing tests to provide a fixed value.
- Priority Level: Low