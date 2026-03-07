[
  {
    "rule_id": "class-level-attribute",
    "severity": "error",
    "message": "Class-level attribute 'users' is shared across all instances, causing unintended state sharing.",
    "line": 8,
    "suggestion": "Move 'users' to instance-level by defining it in __init__."
  },
  {
    "rule_id": "file-open-without-context",
    "severity": "warning",
    "message": "File opened without context manager may leak file descriptors.",
    "line": 28,
    "suggestion": "Use 'with open(path) as f:' to ensure proper resource cleanup."
  },
  {
    "rule_id": "empty-exception-handler",
    "severity": "warning",
    "message": "Exception handler does nothing, potentially masking errors.",
    "line": 35,
    "suggestion": "Log the exception or re-raise with context."
  },
  {
    "rule_id": "default-mutable-arg",
    "severity": "warning",
    "message": "Default mutable argument 'data' may lead to unexpected behavior due to shared list across calls.",
    "line": 49,
    "suggestion": "Use 'None' as default and initialize the list inside the function."
  },
  {
    "rule_id": "side-effect-mutation",
    "severity": "warning",
    "message": "Function mutates the input 'data' list, which is unexpected.",
    "line": 54,
    "suggestion": "Avoid mutating input and return a new list instead."
  },
  {
    "rule_id": "unhandled-return-value",
    "severity": "warning",
    "message": "Caller of 'load_users' does not check for None return value.",
    "line": 63,
    "suggestion": "Check the return value of 'load_users' for None and handle appropriately."
  },
  {
    "rule_id": "missing-docstring",
    "severity": "info",
    "message": "Missing docstring for class 'UserService'.",
    "line": 7,
    "suggestion": "Add a docstring explaining class purpose and usage."
  },
  {
    "rule_id": "missing-docstring",
    "severity": "info",
    "message": "Missing docstring for method '__init__'.",
    "line": 9,
    "suggestion": "Add a docstring describing parameters and initialization behavior."
  },
  {
    "rule_id": "missing-docstring",
    "severity": "info",
    "message": "Missing docstring for method 'load_users'.",
    "line": 14,
    "suggestion": "Add a docstring describing parameters, return value, and behavior."
  },
  {
    "rule_id": "missing-docstring",
    "severity": "info",
    "message": "Missing docstring for method '_load_from_file'.",
    "line": 25,
    "suggestion": "Add a docstring explaining file loading logic and error handling."
  },
  {
    "rule_id": "missing-docstring",
    "severity": "info",
    "message": "Missing docstring for method '_load_random_users'.",
    "line": 39,
    "suggestion": "Add a docstring describing random user generation behavior."
  },
  {
    "rule_id": "missing-docstring",
    "severity": "info",
    "message": "Missing docstring for function 'process'.",
    "line": 49,
    "suggestion": "Add a docstring explaining parameters, side effects, and return value."
  },
  {
    "rule_id": "missing-docstring",
    "severity": "info",
    "message": "Missing docstring for function 'main'.",
    "line": 61,
    "suggestion": "Add a docstring describing main execution flow and purpose."
  },
  {
    "rule_id": "unnecessary-sleep",
    "severity": "warning",
    "message": "Unnecessary sleep in random user generation causes delays.",
    "line": 42,
    "suggestion": "Remove sleep as it serves no purpose in random name generation."
  }
]