```json
[
  {
    "rule_id": "no-global-variables",
    "severity": "warning",
    "message": "Use of global variable 'GLOBAL_RESULTS' reduces modularity and testability.",
    "line": 5,
    "suggestion": "Pass results as parameters or return them from functions."
  },
  {
    "rule_id": "no-duplicate-code",
    "severity": "warning",
    "message": "Duplicate HTTP request logic in get_users, get_posts, and get_comments.",
    "line": 10,
    "suggestion": "Refactor into a reusable helper function."
  },
  {
    "rule_id": "no-bare-except",
    "severity": "error",
    "message": "Catching generic Exception without handling specific cases may mask errors.",
    "line": 10,
    "suggestion": "Catch more specific exceptions like requests.RequestException."
  },
  {
    "rule_id": "no-magic-numbers",
    "severity": "warning",
    "message": "Magic numbers used in conditional checks (e.g., 10, 50).",
    "line": 32,
    "suggestion": "Define constants for these values to improve readability."
  },
  {
    "rule_id": "no-print-statements",
    "severity": "warning",
    "message": "Using print statements instead of logging makes output harder to control.",
    "line": 15,
    "suggestion": "Replace print calls with logging module."
  },
  {
    "rule_id": "no-hardcoded-urls",
    "severity": "warning",
    "message": "Hardcoded URL endpoint makes testing and configuration difficult.",
    "line": 3,
    "suggestion": "Externalize URLs into environment variables or config files."
  }
]
```