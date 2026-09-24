```json
[
  {
    "rule_id": "single-responsibility",
    "severity": "warning",
    "message": "Function 'process_user_input' performs both business logic (validation/authorization) and I/O (printing).",
    "line": 1,
    "suggestion": "Separate the logic for determining access from the logic that prints the result."
  },
  {
    "rule_id": "predictable-interface",
    "severity": "warning",
    "message": "Function 'secret_behavior' depends on a hidden global flag 'hidden_flag', making its behavior implicit.",
    "line": 11,
    "suggestion": "Pass the flag as an explicit parameter to the function."
  },
  {
    "rule_id": "implicit-truthiness",
    "severity": "info",
    "message": "Function 'check_value' relies on implicit truthiness of 'val'.",
    "line": 17,
    "suggestion": "Use an explicit comparison (e.g., 'if val is not None:') to avoid bugs with empty strings or zeros."
  },
  {
    "rule_id": "descriptive-naming",
    "severity": "info",
    "message": "Function name 'f' is not descriptive and does not reflect its intent.",
    "line": 23,
    "suggestion": "Rename 'f' to something more meaningful, such as 'calculate_offset_value'."
  },
  {
    "rule_id": "shared-mutable-state",
    "severity": "warning",
    "message": "Use of global mutable state 'global_config' can introduce hidden coupling.",
    "line": 30,
    "suggestion": "Pass configuration as an argument to 'run_task' or encapsulate it in a config object."
  },
  {
    "rule_id": "environment-dependency",
    "severity": "warning",
    "message": "Direct call to 'time.time()' makes the function non-deterministic and difficult to test.",
    "line": 37,
    "suggestion": "Inject the time as a parameter or use a provider abstraction."
  },
  {
    "rule_id": "no-eval",
    "severity": "error",
    "message": "Use of 'eval' on user-provided input is a critical security risk.",
    "line": 40,
    "suggestion": "Avoid 'eval'. Use a safe alternative like 'ast.literal_eval' or a predefined mapping of allowed operations."
  },
  {
    "rule_id": "broad-exception",
    "severity": "warning",
    "message": "Catching a broad 'Exception' can hide unexpected bugs and make debugging difficult.",
    "line": 44,
    "suggestion": "Catch specific exceptions, such as 'KeyError' or 'TypeError'."
  },
  {
    "rule_id": "mutate-input",
    "severity": "warning",
    "message": "Function 'risky_update' modifies the input dictionary 'data' in place without documentation.",
    "line": 43,
    "suggestion": "Create a copy of the data or document that the input is mutated."
  }
]
```