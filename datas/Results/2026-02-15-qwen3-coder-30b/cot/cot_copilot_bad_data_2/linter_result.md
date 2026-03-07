[
  {
    "rule_id": "no-console",
    "severity": "warning",
    "message": "Unexpected console output in function 'process_user_input'. I/O operations should be separated from business logic.",
    "line": 4,
    "suggestion": "Extract logging or printing into a separate function or pass logger as dependency."
  },
  {
    "rule_id": "no-console",
    "severity": "warning",
    "message": "Unexpected console output in function 'process_user_input'. I/O operations should be separated from business logic.",
    "line": 6,
    "suggestion": "Extract logging or printing into a separate function or pass logger as dependency."
  },
  {
    "rule_id": "no-console",
    "severity": "warning",
    "message": "Unexpected console output in function 'secret_behavior'. I/O operations should be separated from business logic.",
    "line": 12,
    "suggestion": "Extract logging or printing into a separate function or pass logger as dependency."
  },
  {
    "rule_id": "no-console",
    "severity": "warning",
    "message": "Unexpected console output in function 'run_task'. I/O operations should be separated from business logic.",
    "line": 27,
    "suggestion": "Extract logging or printing into a separate function or pass logger as dependency."
  },
  {
    "rule_id": "no-console",
    "severity": "warning",
    "message": "Unexpected console output in function 'run_task'. I/O operations should be separated from business logic.",
    "line": 29,
    "suggestion": "Extract logging or printing into a separate function or pass logger as dependency."
  },
  {
    "rule_id": "no-unsafe-eval",
    "severity": "error",
    "message": "Usage of 'eval' in function 'unsafe_eval' poses a high security risk due to arbitrary code execution.",
    "line": 32,
    "suggestion": "Avoid 'eval'; use safer alternatives like AST parsing or whitelisted function dispatch."
  },
  {
    "rule_id": "no-magic-numbers",
    "severity": "warning",
    "message": "Magic number '7' used in function 'f'. Should be replaced with named constant for clarity.",
    "line": 18,
    "suggestion": "Define '7' as a named constant or parameter to improve readability."
  },
  {
    "rule_id": "no-magic-numbers",
    "severity": "warning",
    "message": "Magic number '13' used in function 'f'. Should be replaced with named constant for clarity.",
    "line": 18,
    "suggestion": "Define '13' as a named constant or parameter to improve readability."
  },
  {
    "rule_id": "no-global-state",
    "severity": "warning",
    "message": "Use of global variable 'global_config' makes function 'run_task' dependent on external state.",
    "line": 24,
    "suggestion": "Pass configuration as an explicit parameter to avoid tight coupling."
  },
  {
    "rule_id": "no-side-effects-in-logic",
    "severity": "warning",
    "message": "Function 'check_value' uses truthiness checks which may mask logical inconsistencies.",
    "line": 15,
    "suggestion": "Use explicit comparison (e.g., `if val is not None`) to clarify intent."
  },
  {
    "rule_id": "no-shared-mutable-state",
    "severity": "warning",
    "message": "Shared mutable global state through 'global_config' increases complexity and test difficulty.",
    "line": 23,
    "suggestion": "Pass mutable configuration as an argument or encapsulate in a config object."
  },
  {
    "rule_id": "no-duplicate-code",
    "severity": "warning",
    "message": "Similar conditional logic exists in multiple places (e.g., access control). Consider abstraction.",
    "line": 6,
    "suggestion": "Refactor similar checks into reusable helper functions."
  }
]