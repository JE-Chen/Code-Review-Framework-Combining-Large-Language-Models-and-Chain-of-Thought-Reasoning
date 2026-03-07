[
  {
    "rule_id": "bad-global-name",
    "severity": "warning",
    "message": "Mutable global variable 'DATA' named in uppercase (typically for constants)",
    "line": 6,
    "suggestion": "Rename to lowercase and avoid global state; use dependency injection"
  },
  {
    "rule_id": "bad-global-name",
    "severity": "warning",
    "message": "Mutable global variable 'RESULTS' named in uppercase (typically for constants)",
    "line": 7,
    "suggestion": "Rename to lowercase and avoid global state; use dependency injection"
  },
  {
    "rule_id": "missing-docstring",
    "severity": "warning",
    "message": "Function 'home' lacks docstring describing endpoint behavior",
    "line": 11,
    "suggestion": "Add docstring explaining response content and purpose"
  },
  {
    "rule_id": "bad-variable-name",
    "severity": "warning",
    "message": "Variable 'meanVal' uses inconsistent naming; prefer 'mean' or 'mean_value'",
    "line": 27,
    "suggestion": "Rename to 'mean' for semantic clarity"
  },
  {
    "rule_id": "redundant-computation",
    "severity": "warning",
    "message": "Mean computed twice for same data; reuse existing variable",
    "line": 29,
    "suggestion": "Replace with: RESULTS['meanAgain'] = meanVal"
  },
  {
    "rule_id": "bad-key-name",
    "severity": "warning",
    "message": "Key 'meanAgain' is confusing and redundant",
    "line": 29,
    "suggestion": "Remove redundant key or choose meaningful name"
  },
  {
    "rule_id": "redundant-computation",
    "severity": "warning",
    "message": "Median computed twice for same data; reuse existing variable",
    "line": 36,
    "suggestion": "Store median in variable and reuse for both keys"
  }
]