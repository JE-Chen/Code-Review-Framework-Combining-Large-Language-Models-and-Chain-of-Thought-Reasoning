[
  {
    "rule_id": "no-global-state",
    "severity": "warning",
    "message": "Global variable 'DATA_STORE' defined. Avoid global state for better testability and modularity.",
    "line": 5,
    "suggestion": "Use dependency injection or a class instance to manage state."
  },
  {
    "rule_id": "no-global-state",
    "severity": "warning",
    "message": "Global variable 'USER_COUNT' defined. Avoid global state for better testability and modularity.",
    "line": 6,
    "suggestion": "Use dependency injection or a class instance to manage state."
  },
  {
    "rule_id": "no-global-state",
    "severity": "warning",
    "message": "Global variable 'CONFIG' defined. Avoid global state for better testability and modularity.",
    "line": 7,
    "suggestion": "Use dependency injection or a class instance to manage configuration."
  },
  {
    "rule_id": "missing-docstring",
    "severity": "info",
    "message": "Route function 'index' lacks a docstring.",
    "line": 9,
    "suggestion": "Add a docstring describing the route and its behavior."
  },
  {
    "rule_id": "missing-docstring",
    "severity": "info",
    "message": "Route function 'add_item' lacks a docstring.",
    "line": 13,
    "suggestion": "Add a docstring describing the route parameters and expected behavior."
  },
  {
    "rule_id": "missing-param-validation",
    "severity": "warning",
    "message": "Parameter 'item' not validated for presence in request.",
    "line": 17,
    "suggestion": "Validate required parameters and return 400 if missing."
  },
  {
    "rule_id": "missing-docstring",
    "severity": "info",
    "message": "Route function 'get_items' lacks a docstring.",
    "line": 24,
    "suggestion": "Add a docstring describing the route and its parameters."
  },
  {
    "rule_id": "missing-docstring",
    "severity": "info",
    "message": "Route function 'reset_data' lacks a docstring.",
    "line": 37,
    "suggestion": "Add a docstring describing the route's purpose and side effects."
  },
  {
    "rule_id": "invalid-config-mutation",
    "severity": "error",
    "message": "CONFIG['mode'] set to 'reset' which is not handled in get_items logic.",
    "line": 42,
    "suggestion": "Reset CONFIG['mode'] to a valid value or remove the assignment."
  },
  {
    "rule_id": "missing-docstring",
    "severity": "info",
    "message": "Route function 'complex_route' lacks a docstring.",
    "line": 45,
    "suggestion": "Add a docstring describing the route parameters and return values."
  },
  {
    "rule_id": "complex-logic",
    "severity": "warning",
    "message": "Complex condition in /complex route with deep nesting and redundant checks.",
    "line": 48,
    "suggestion": "Simplify conditionals and consider breaking into helper functions."
  }
]