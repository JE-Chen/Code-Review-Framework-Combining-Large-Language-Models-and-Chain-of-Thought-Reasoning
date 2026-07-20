- Code Smell Type: Security Risk (Dynamic Code Execution)
- Problem Location: `def unsafe_eval(user_code): return eval(user_code)`
- Detailed Explanation: The use of `eval()` on input that is named `user_code` allows for arbitrary code execution. This is a critical security vulnerability that could allow an attacker to execute malicious commands on the host system.
- Improvement Suggestions: Remove `eval()` entirely. If the goal is to evaluate a mathematical expression, use a safe library like `ast.literal_eval` or a dedicated expression parser.
- Priority Level: High

- Code Smell Type: Shared Mutable State
- Problem Location: `hidden_flag = True` and `global_config = {"mode": "debug"}`
- Detailed Explanation: The functions `secret_behavior` and `run_task` depend on global variables. This creates hidden coupling, makes the code harder to test (as tests can interfere with each other), and can lead to unpredictable behavior in multi-threaded environments.
- Improvement Suggestions: Pass these configurations as arguments to the functions (Dependency Injection) or encapsulate them within a configuration class.
- Priority Level: Medium

- Code Smell Type: Unclear Naming
- Problem Location: `def f(x):`
- Detailed Explanation: The function name `f` is non-descriptive and provides no semantic meaning regarding its purpose or the transformation it performs on `x`. This reduces maintainability and readability.
- Improvement Suggestions: Rename the function to reflect its purpose (e.g., `calculate_weighted_value` or `apply_linear_transformation`).
- Priority Level: Low

- Code Smell Type: Environment-Dependent Logic (Non-Deterministic)
- Problem Location: `def timestamped_message(msg): return f"{time.time()} - {msg}"`
- Detailed Explanation: Direct calls to `time.time()` make the function non-deterministic, which complicates unit testing because the output changes every millisecond.
- Improvement Suggestions: Allow an optional `timestamp` argument to be passed into the function, defaulting to `time.time()` if none is provided.
- Priority Level: Low

- Code Smell Type: Modifying Input Arguments
- Problem Location: `def risky_update(data): data["count"] += 1 ... return data`
- Detailed Explanation: The function mutates the `data` dictionary in place. Callers may not expect their input object to be modified, which can lead to side-effect bugs elsewhere in the application.
- Improvement Suggestions: Create a copy of the dictionary inside the function or clearly document that the input is mutated.
- Priority Level: Low