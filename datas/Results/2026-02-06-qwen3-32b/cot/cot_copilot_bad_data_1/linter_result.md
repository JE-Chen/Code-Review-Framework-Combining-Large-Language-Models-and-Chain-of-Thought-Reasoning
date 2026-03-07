[
  {
    "rule_id": "mutable_default",
    "severity": "error",
    "message": "Mutable default argument 'container' can lead to unexpected shared state between function calls.",
    "line": 1,
    "suggestion": "Use None as the default and initialize the list inside the function."
  },
  {
    "rule_id": "global_mutable",
    "severity": "warning",
    "message": "Global mutable variable 'shared_list' creates hidden coupling and complicates testing.",
    "line": 4,
    "suggestion": "Prefer passing state explicitly or encapsulating in an object."
  },
  {
    "rule_id": "mutate_input",
    "severity": "warning",
    "message": "Function mutates input argument 'data' without documentation.",
    "line": 11,
    "suggestion": "Return a new list instead of mutating the input."
  },
  {
    "rule_id": "broad_exception",
    "severity": "warning",
    "message": "Catches all exceptions (Exception) instead of specific ones.",
    "line": 36,
    "suggestion": "Catch specific exceptions like ZeroDivisionError."
  },
  {
    "rule_id": "inconsistent_return",
    "severity": "error",
    "message": "Function returns inconsistent types (int and str) based on input.",
    "line": 41,
    "suggestion": "Return consistent types, e.g., always return a string or always return an integer."
  },
  {
    "rule_id": "repeated_computation",
    "severity": "warning",
    "message": "Repeated calculation of len(values) inside the loop.",
    "line": 48,
    "suggestion": "Precompute the length and use it in the condition."
  },
  {
    "rule_id": "side_effect_in_comprehension",
    "severity": "warning",
    "message": "List comprehension used for side effect (print) instead of building a collection.",
    "line": 52,
    "suggestion": "Use an explicit for loop for side effects."
  },
  {
    "rule_id": "unsafe_eval",
    "severity": "error",
    "message": "Use of eval() introduces security risks and is generally unsafe.",
    "line": 58,
    "suggestion": "Avoid eval() and use safer alternatives for code execution."
  }
]