[
  {
    "rule_id": "no-global-mutation",
    "severity": "warning",
    "message": "Global variables like DATA_STORE, USER_COUNT, and CONFIG are mutated directly, which can lead to unpredictable state changes.",
    "line": 6,
    "suggestion": "Use a dedicated data manager or service layer to encapsulate mutable state."
  },
  {
    "rule_id": "no-raw-exceptions",
    "severity": "error",
    "message": "Catching a generic Exception without logging or re-raising may hide critical errors.",
    "line": 15,
    "suggestion": "Log the exception before returning it or re-raise with more context."
  },
  {
    "rule_id": "no-duplicated-logic",
    "severity": "warning",
    "message": "The same logic block for appending items exists in multiple routes; consider refactoring into a helper function.",
    "line": 14,
    "suggestion": "Extract common logic into reusable functions."
  },
  {
    "rule_id": "no-hardcoded-config",
    "severity": "warning",
    "message": "Configuration values like 'mode' and 'threshold' are hardcoded instead of using environment variables.",
    "line": 6,
    "suggestion": "Move configuration to external settings or environment variables."
  },
  {
    "rule_id": "no-nested-conditionals",
    "severity": "warning",
    "message": "Deeply nested conditionals in complex_route reduce readability and increase chance of logical errors.",
    "line": 39,
    "suggestion": "Refactor nested conditions using early returns or helper functions."
  },
  {
    "rule_id": "no-unvalidated-input",
    "severity": "error",
    "message": "User input from request.args is used without validation, risking unexpected behavior.",
    "line": 38,
    "suggestion": "Validate and sanitize all inputs before processing."
  },
  {
    "rule_id": "no-magic-numbers",
    "severity": "warning",
    "message": "Magic numbers like 100 and 10 appear in logic without explanation.",
    "line": 39,
    "suggestion": "Replace magic numbers with named constants."
  }
]