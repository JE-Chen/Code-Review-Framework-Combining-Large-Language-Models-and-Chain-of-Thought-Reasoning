```json
[
  {
    "rule_id": "mutable-default-argument",
    "severity": "error",
    "message": "Function 'process_items' uses a mutable default argument (items=[]). This can lead to shared state between function calls.",
    "line": 7,
    "suggestion": "Use 'items=None' and initialize to '[]' inside the function."
  },
  {
    "rule_id": "shared-mutable-state",
    "severity": "warning",
    "message": "The 'cache' and 'results' variables are defined at the module level and mutated within functions, creating hidden coupling.",
    "line": 4,
    "suggestion": "Encapsulate state within a class or pass it explicitly as function arguments."
  },
  {
    "rule_id": "side-effect-in-comprehension",
    "severity": "warning",
    "message": "List comprehension used for side effect (appending to 'results') rather than creating a collection.",
    "line": 14,
    "suggestion": "Use a standard 'results.append(cache[item])' call."
  },
  {
    "rule_id": "deeply-nested-logic",
    "severity": "info",
    "message": "Nested conditional logic for 'verbose' and 'len(results)' increases cognitive load.",
    "line": 16,
    "suggestion": "Use a guard clause or combine conditions: 'if verbose and len(results) > 10:'."
  },
  {
    "rule_id": "inconsistent-return-types",
    "severity": "warning",
    "message": "Function 'expensive_compute' returns multiple types: None, string, and integer.",
    "line": 21,
    "suggestion": "Ensure the function returns a consistent type or use a Union type with clear documentation."
  },
  {
    "rule_id": "security-risk-eval",
    "severity": "error",
    "message": "Use of 'eval' for computation is a security risk and inefficient.",
    "line": 26,
    "suggestion": "Replace 'eval(f\"{x} * {x}\")' with 'x * x'."
  },
  {
    "rule_id": "broad-exception-handling",
    "severity": "warning",
    "message": "Catching broad 'Exception' can hide unexpected bugs and make debugging difficult.",
    "line": 27,
    "suggestion": "Catch specific exceptions (e.g., TypeError, ValueError)."
  },
  {
    "rule_id": "unvalidated-external-input",
    "severity": "warning",
    "message": "User input is used as a key in the 'cache' dictionary without sufficient validation or sanitization.",
    "line": 31,
    "suggestion": "Validate that 'user_input' conforms to expected types or constraints before using it."
  }
]
```