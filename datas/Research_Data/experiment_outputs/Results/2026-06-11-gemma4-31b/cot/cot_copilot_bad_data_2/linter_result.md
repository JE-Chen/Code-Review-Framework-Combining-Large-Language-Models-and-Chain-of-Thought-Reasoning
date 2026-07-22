```json
[
  {
    "rule_id": "single-responsibility",
    "severity": "warning",
    "message": "Function 'process_user_input' performs both business logic (validation/authorization) and I/O (printing).",
    "line": 1,
    "suggestion": "Separate the logic that determines access from the logic that notifies the user."
  },
  {
    "rule_id": "implicit-context",
    "severity": "error",
    "message": "Function 'secret_behavior' depends on a global variable 'hidden_flag', making its behavior unpredictable and hard to test.",
    "line": 11,
    "suggestion": "Pass 'hidden_flag' as an explicit parameter to the function."
  },
  {
    "rule_id": "implicit-truthiness",
    "severity": "warning",
    "message": "Function 'check_value' relies on implicit truthiness of 'val'. This can lead to bugs if 'val' is 0, an empty string, or an empty list.",
    "line": 17,
    "suggestion": "Use explicit comparisons (e.g., 'if val is not None:')."
  },
  {
    "rule_id": "descriptive-naming",
    "severity": "info",
    "message": "Function name 'f' is non-descriptive and does not reflect the intent of the operation.",
    "line": 23,
    "suggestion": "Rename 'f' to something descriptive, such as 'calculate_offset_value'."
  },
  {
    "rule_id": "shared-mutable-state",
    "severity": "warning",
    "message": "The use of 'global_config' as a module-level mutable dictionary introduces hidden coupling.",
    "line": 29,
    "suggestion": "Encapsulate configuration in a class or pass the config object as a parameter to 'run_task'."
  },
  {
    "rule_id": "environment-dependency",
    "severity": "warning",
    "message": "Direct call to 'time.time()' inside 'timestamped_message' makes the function non-deterministic and difficult to unit test.",
    "line": 36,
    "suggestion": "Inject the current time as a parameter or use a provider/wrapper for time functions."
  },
  {
    "rule_id": "no-dynamic-execution",
    "severity": "error",
    "message": "The use of 'eval()' allows execution of arbitrary code, posing a severe security risk.",
    "line": 39,
    "suggestion": "Avoid 'eval()'. Use a safer alternative like 'ast.literal_eval()' or a predefined mapping of allowed operations."
  },
  {
    "rule_id": "no-input-mutation",
    "severity": "warning",
    "message": "Function 'risky_update' modifies the 'data' input argument directly, which can cause unexpected side effects for the caller.",
    "line": 42,
    "suggestion": "Create a copy of the dictionary or return a new dictionary instead of mutating the input."
  }
]
```