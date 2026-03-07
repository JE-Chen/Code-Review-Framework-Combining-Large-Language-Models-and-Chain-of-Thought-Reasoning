[
  {
    "rule_id": "side-effect-in-pure-function",
    "severity": "error",
    "message": "Function 'process_user_input' performs I/O (print) which should be separated from business logic.",
    "line": 3,
    "suggestion": "Move I/O to the caller or use logging instead."
  },
  {
    "rule_id": "side-effect-in-pure-function",
    "severity": "error",
    "message": "Function 'process_user_input' performs I/O (print) which should be separated from business logic.",
    "line": 6,
    "suggestion": "Move I/O to the caller or use logging instead."
  },
  {
    "rule_id": "side-effect-in-pure-function",
    "severity": "error",
    "message": "Function 'process_user_input' performs I/O (print) which should be separated from business logic.",
    "line": 9,
    "suggestion": "Move I/O to the caller or use logging instead."
  },
  {
    "rule_id": "avoid-global-state",
    "severity": "warning",
    "message": "Function 'secret_behavior' relies on global state (hidden_flag) instead of explicit parameters.",
    "line": 14,
    "suggestion": "Pass hidden_flag as a parameter to the function."
  },
  {
    "rule_id": "avoid-implicit-truthiness",
    "severity": "warning",
    "message": "Function 'check_value' uses implicit truthiness (if val) which may lead to unexpected behavior.",
    "line": 20,
    "suggestion": "Use explicit condition (e.g., if val is not None)."
  },
  {
    "rule_id": "bad-function-name",
    "severity": "warning",
    "message": "Function name 'f' is too generic and does not describe its purpose.",
    "line": 25,
    "suggestion": "Rename to a descriptive name (e.g., 'calculate_factor')."
  },
  {
    "rule_id": "avoid-global-state",
    "severity": "warning",
    "message": "Function 'run_task' relies on global state (global_config) instead of explicit parameters.",
    "line": 32,
    "suggestion": "Pass global_config as a parameter to the function."
  },
  {
    "rule_id": "avoid-time-dependent-logic",
    "severity": "warning",
    "message": "Function 'timestamped_message' uses time-dependent value (time.time()) which makes tests non-deterministic.",
    "line": 38,
    "suggestion": "Pass the current time as a parameter or use dependency injection for time."
  },
  {
    "rule_id": "unsafe-eval",
    "severity": "error",
    "message": "Function 'unsafe_eval' uses 'eval' which is a security risk and should be avoided.",
    "line": 41,
    "suggestion": "Do not use eval; consider safer alternatives for code execution."
  },
  {
    "rule_id": "mutate-input-argument",
    "severity": "warning",
    "message": "Function 'risky_update' modifies the input argument (data) which can cause unexpected side effects.",
    "line": 46,
    "suggestion": "Return a new dictionary instead of mutating the input."
  }
]