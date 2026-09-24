```json
[
  {
    "rule_id": "shared-mutable-state",
    "severity": "warning",
    "message": "Use of shared mutable state at the module level ('global_config') can introduce hidden coupling and make testing difficult.",
    "line": 31,
    "suggestion": "Pass configuration explicitly as an argument to functions or encapsulate it in a configuration object."
  },
  {
    "rule_id": "environment-dependent-logic",
    "severity": "warning",
    "message": "Direct call to 'time.time()' makes the function non-deterministic and difficult to unit test.",
    "line": 39,
    "suggestion": "Inject a clock provider or pass the timestamp as an argument to the function."
  },
  {
    "rule_id": "no-eval",
    "severity": "error",
    "message": "Use of 'eval' introduces serious security risks (Remote Code Execution) and makes the code harder to reason about.",
    "line": 42,
    "suggestion": "Avoid dynamic code execution. Use a safe parser, a dictionary mapping, or a dedicated expression language if dynamic evaluation is required."
  },
  {
    "rule_id": "mutate-input-argument",
    "severity": "warning",
    "message": "The function 'risky_update' modifies the input dictionary 'data' in place, which can lead to unexpected side effects for the caller.",
    "line": 45,
    "suggestion": "Create a copy of the data before modifying it or return a new dictionary."
  }
]
```