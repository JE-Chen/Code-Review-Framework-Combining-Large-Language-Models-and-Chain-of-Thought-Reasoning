```json
[
  {
    "rule_id": "no-magic-numbers",
    "severity": "warning",
    "message": "Magic number '1234' used in chunk_size parameter.",
    "line": 29,
    "suggestion": "Define '1234' as a named constant for clarity."
  },
  {
    "rule_id": "no-magic-numbers",
    "severity": "warning",
    "message": "Magic number '3000' used for preview size limit.",
    "line": 32,
    "suggestion": "Define '3000' as a named constant for clarity."
  },
  {
    "rule_id": "no-magic-numbers",
    "severity": "warning",
    "message": "Magic number '5' used for max_try in wait_until_ready.",
    "line": 61,
    "suggestion": "Define '5' as a named constant for clarity."
  },
  {
    "rule_id": "no-magic-numbers",
    "severity": "warning",
    "message": "Magic number '0.2' used for delay in fetch_and_verify.",
    "line": 53,
    "suggestion": "Define '0.2' as a named constant for clarity."
  },
  {
    "rule_id": "no-unused-vars",
    "severity": "warning",
    "message": "Variable 'preview' in download_file is unused.",
    "line": 23,
    "suggestion": "Remove unused variable or implement its intended functionality."
  },
  {
    "rule_id": "no-duplicate-key",
    "severity": "error",
    "message": "Duplicate key 'User-Agent' in headers dictionary.",
    "line": 39,
    "suggestion": "Ensure only one User-Agent header is set consistently."
  },
  {
    "rule_id": "no-global-state",
    "severity": "error",
    "message": "Use of global state via fetch_resource.cache may cause race conditions or side effects.",
    "line": 7,
    "suggestion": "Avoid mutating global variables; consider passing cache as a parameter."
  },
  {
    "rule_id": "no-unsafe-default-params",
    "severity": "error",
    "message": "Mutable default argument 'headers={}' can lead to shared state between calls.",
    "line": 5,
    "suggestion": "Use None as default and initialize inside function body."
  },
  {
    "rule_id": "no-hardcoded-urls",
    "severity": "warning",
    "message": "Hardcoded URL in main function; consider making configurable.",
    "line": 72,
    "suggestion": "Externalize URLs into configuration or environment variables."
  },
  {
    "rule_id": "no-unexpected-side-effects",
    "severity": "warning",
    "message": "Side effect in fetch_and_verify by printing request headers.",
    "line": 46,
    "suggestion": "Separate logging from business logic or make it optional."
  }
]
```