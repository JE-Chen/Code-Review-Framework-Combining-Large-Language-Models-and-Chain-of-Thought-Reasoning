```json
[
  {
    "rule_id": "broad-exception",
    "severity": "warning",
    "message": "Avoid catching broad exceptions such as `except Exception:`. This can hide real bugs and make debugging difficult.",
    "line": 7,
    "suggestion": "Catch specific exception types that are expected during division."
  },
  {
    "rule_id": "inconsistent-return-types",
    "severity": "warning",
    "message": "Function returns different types (float/int and int) depending on conditions, which increases the burden on callers.",
    "line": 3,
    "suggestion": "Ensure consistent return types or raise a custom exception for error states."
  },
  {
    "rule_id": "broad-exception",
    "severity": "warning",
    "message": "Avoid catching broad exceptions such as `except Exception:`. This can hide real bugs.",
    "line": 15,
    "suggestion": "Catch specific exceptions related to type conversion."
  },
  {
    "rule_id": "inconsistent-return-types",
    "severity": "warning",
    "message": "Function returns different types (int and int) but uses magic numbers (-999, 0) to signal different error states.",
    "line": 13,
    "suggestion": "Consider raising an exception or returning None to indicate failure."
  },
  {
    "rule_id": "broad-exception",
    "severity": "warning",
    "message": "Avoid catching broad exceptions such as `except Exception:`. This can hide real bugs.",
    "line": 26,
    "suggestion": "Catch specific I/O exceptions."
  },
  {
    "rule_id": "inconsistent-return-types",
    "severity": "warning",
    "message": "Function returns different types (string data and error strings like 'FILE_NOT_FOUND').",
    "line": 24,
    "suggestion": "Return None or raise an exception for missing files instead of a magic string."
  },
  {
    "rule_id": "deeply-nested-logic",
    "severity": "warning",
    "message": "Deeply nested conditional/try-except logic reduces readability and increases cognitive load.",
    "line": 31,
    "suggestion": "Refactor the inner logic into a separate function or use guard clauses."
  },
  {
    "rule_id": "broad-exception",
    "severity": "warning",
    "message": "Avoid catching broad exceptions such as `except Exception:`. This can hide real bugs.",
    "line": 33,
    "suggestion": "Catch specific exceptions during data splitting/conversion."
  },
  {
    "rule_id": "broad-exception",
    "severity": "warning",
    "message": "Avoid catching broad exceptions such as `except Exception:`. This can hide real bugs.",
    "line": 38,
    "suggestion": "Catch specific exceptions or rely on the error handling inside `risky_division`."
  },
  {
    "rule_id": "broad-exception",
    "severity": "warning",
    "message": "Avoid catching broad exceptions such as `except Exception:`. This can hide real bugs.",
    "line": 41,
    "suggestion": "Catch specific exceptions."
  },
  {
    "rule_id": "broad-exception",
    "severity": "warning",
    "message": "Avoid catching broad exceptions such as `except Exception:`. This can hide real bugs.",
    "line": 48,
    "suggestion": "Catch specific exceptions."
  }
]
```