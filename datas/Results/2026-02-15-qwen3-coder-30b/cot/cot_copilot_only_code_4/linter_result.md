[
  {
    "rule_id": "no-broad-exception",
    "severity": "error",
    "message": "Catching broad exception type 'Exception' can hide unexpected errors and make debugging harder.",
    "line": 6,
    "suggestion": "Catch more specific exception types like 'ValueError' or handle general cases explicitly."
  },
  {
    "rule_id": "no-broad-exception",
    "severity": "error",
    "message": "Catching broad exception type 'Exception' can hide unexpected errors and make debugging harder.",
    "line": 15,
    "suggestion": "Catch more specific exception types like 'FileNotFoundError' or handle general cases explicitly."
  },
  {
    "rule_id": "no-broad-exception",
    "severity": "error",
    "message": "Catching broad exception type 'Exception' can hide unexpected errors and make debugging harder.",
    "line": 23,
    "suggestion": "Catch more specific exception types instead of using a generic 'Exception'."
  },
  {
    "rule_id": "no-broad-exception",
    "severity": "error",
    "message": "Catching broad exception type 'Exception' can hide unexpected errors and make debugging harder.",
    "line": 27,
    "suggestion": "Catch more specific exception types instead of using a generic 'Exception'."
  },
  {
    "rule_id": "no-broad-exception",
    "severity": "error",
    "message": "Catching broad exception type 'Exception' can hide unexpected errors and make debugging harder.",
    "line": 32,
    "suggestion": "Catch more specific exception types instead of using a generic 'Exception'."
  },
  {
    "rule_id": "inconsistent-return-types",
    "severity": "error",
    "message": "Function returns inconsistent types (int, str, None) which increases caller complexity and risk of runtime errors.",
    "line": 2,
    "suggestion": "Ensure consistent return types across all execution paths."
  },
  {
    "rule_id": "inconsistent-return-types",
    "severity": "error",
    "message": "Function returns inconsistent types (int, str, None) which increases caller complexity and risk of runtime errors.",
    "line": 10,
    "suggestion": "Ensure consistent return types across all execution paths."
  },
  {
    "rule_id": "inconsistent-return-types",
    "severity": "error",
    "message": "Function returns inconsistent types (int, str, None) which increases caller complexity and risk of runtime errors.",
    "line": 19,
    "suggestion": "Ensure consistent return types across all execution paths."
  },
  {
    "rule_id": "inconsistent-return-types",
    "severity": "error",
    "message": "Function returns inconsistent types (int, str, None) which increases caller complexity and risk of runtime errors.",
    "line": 29,
    "suggestion": "Ensure consistent return types across all execution paths."
  },
  {
    "rule_id": "no-resource-leak",
    "severity": "warning",
    "message": "File handle is not properly managed; consider using context manager ('with') to ensure proper closure.",
    "line": 17,
    "suggestion": "Use 'with open(...)' to automatically manage file resources."
  }
]