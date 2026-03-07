[
  {
    "rule_id": "no-magic-numbers",
    "severity": "warning",
    "message": "The number 3.14159 is used directly; consider defining it as a constant for better readability and maintainability.",
    "line": 38,
    "suggestion": "Define PI as a named constant at the top of the module."
  },
  {
    "rule_id": "no-unsafe-eval",
    "severity": "error",
    "message": "Use of eval() can introduce security vulnerabilities through code injection attacks.",
    "line": 40,
    "suggestion": "Avoid using eval(). Consider alternative approaches such as using ast.literal_eval() for safe evaluation of literals."
  },
  {
    "rule_id": "no-global-assign",
    "severity": "error",
    "message": "Assignment to global variable 'shared_list' inside function 'append_global' modifies a global state, which can lead to unpredictable behavior.",
    "line": 11,
    "suggestion": "Refactor to avoid modifying global variables. Pass 'shared_list' as a parameter or use a class-based approach."
  },
  {
    "rule_id": "no-duplicate-key",
    "severity": "warning",
    "message": "The list comprehension on line 33 creates side effects by calling print(), which violates functional programming principles.",
    "line": 33,
    "suggestion": "Separate concerns: do not perform I/O operations within list comprehensions."
  },
  {
    "rule_id": "no-implicit-coercion",
    "severity": "warning",
    "message": "Inconsistent return types in 'inconsistent_return': returns integer when flag=True, string otherwise. This may cause confusion.",
    "line": 26,
    "suggestion": "Ensure consistent return types across all branches of the function."
  },
  {
    "rule_id": "no-nested-conditional",
    "severity": "warning",
    "message": "Deeply nested conditional logic in 'nested_conditions' makes code harder to read and debug.",
    "line": 16,
    "suggestion": "Refactor nested conditions into simpler, more readable logic using early returns or helper functions."
  },
  {
    "rule_id": "no-undefined-var",
    "severity": "error",
    "message": "Default argument 'container=[]' uses a mutable default value, leading to unexpected behavior due to shared state between calls.",
    "line": 1,
    "suggestion": "Use None as default and initialize the list inside the function body instead."
  },
  {
    "rule_id": "no-exception-raised",
    "severity": "warning",
    "message": "Catching generic Exception in 'risky_division' prevents proper error handling and hides underlying issues.",
    "line": 21,
    "suggestion": "Catch specific exceptions like ZeroDivisionError instead of the broad Exception class."
  },
  {
    "rule_id": "no-loop-func",
    "severity": "warning",
    "message": "Loop variable 'v' is compared against 'len(values)' in 'compute_in_loop', but this condition might be inefficient or incorrect depending on intent.",
    "line": 30,
    "suggestion": "Clarify whether comparison should be against length or another metric. Consider optimizing or clarifying the loop logic."
  }
]