```json
[
  {
    "rule_id": "shared-mutable-state",
    "severity": "error",
    "message": "The use of a global mutable dictionary 'GLOBAL_STATE' introduces hidden coupling and makes the code difficult to test and reason about.",
    "line": 1,
    "suggestion": "Encapsulate the state within a class or pass the state explicitly as an argument to the functions."
  },
  {
    "rule_id": "shared-mutable-state",
    "severity": "warning",
    "message": "Function 'init_data' mutates global state directly.",
    "line": 9,
    "suggestion": "Return a new state object or use a class method to initialize instance state."
  },
  {
    "rule_id": "shared-mutable-state",
    "severity": "warning",
    "message": "Function 'increment_counter' mutates global state directly.",
    "line": 13,
    "suggestion": "Pass the counter as an argument and return the incremented value."
  },
  {
    "rule_id": "shared-mutable-state",
    "severity": "warning",
    "message": "Function 'toggle_flag' mutates global state directly.",
    "line": 17,
    "suggestion": "Pass the flag as an argument and return the toggled value."
  },
  {
    "rule_id": "shared-mutable-state",
    "severity": "warning",
    "message": "Function 'process_items' relies on multiple global state variables, making it impure and harder to unit test.",
    "line": 21,
    "suggestion": "Pass 'data', 'flag', and 'threshold' as explicit parameters to the function."
  },
  {
    "rule_id": "shared-mutable-state",
    "severity": "warning",
    "message": "Function 'reset_state' mutates global state directly.",
    "line": 36,
    "suggestion": "Return a default state configuration instead of mutating a global object."
  }
]
```