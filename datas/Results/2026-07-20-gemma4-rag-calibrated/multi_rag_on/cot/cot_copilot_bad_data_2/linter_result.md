```json
[
  {
    "rule_id": "shared-mutable-state",
    "severity": "warning",
    "message": "The variable 'hidden_flag' is a shared mutable state at the module level, which can lead to hidden coupling and make behavior difficult to reason about.",
    "line": 12,
    "suggestion": "Encapsulate the flag within a class or pass it as an explicit argument to the function."
  },
  {
    "rule_id": "meaningless-naming",
    "severity": "info",
    "message": "Function name 'f' is not descriptive or meaningful.",
    "line": 25,
    "suggestion": "Rename the function to reflect its purpose (e.g., 'calculate_linear_transform')."
  },
  {
    "rule_id": "shared-mutable-state",
    "severity": "warning",
    "message": "The variable 'global_config' is a shared mutable dictionary at the module level.",
    "line": 31,
    "suggestion": "Use a configuration object or pass settings explicitly to functions."
  },
  {
    "rule_id": "environment-dependent-logic",
    "severity": "warning",
    "message": "Direct call to 'time.time()' makes the function non-deterministic and difficult to test.",
    "line": 39,
    "suggestion": "Inject a clock provider or pass the timestamp as an argument."
  },
  {
    "rule_id": "no-dynamic-execution",
    "severity": "error",
    "message": "Use of 'eval' introduces serious security risks and makes the code harder to reason about.",
    "line": 42,
    "suggestion": "Avoid dynamic code execution; use a safe parser or a predefined mapping of allowed operations."
  },
  {
    "rule_id": "mutate-input-argument",
    "severity": "warning",
    "message": "The function 'risky_update' modifies the input 'data' dictionary in place without documentation.",
    "line": 45,
    "suggestion": "Create a copy of the data or return a new dictionary to avoid side effects for the caller."
  }
]
```