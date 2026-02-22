```json
[
  {
    "rule_id": "no-unused-vars",
    "severity": "warning",
    "message": "Variable 'n' in step2_filter_even is unused after the condition check.",
    "line": 5,
    "suggestion": "Simplify the condition to remove redundant checks like `n != 0` and `n > -9999`."
  },
  {
    "rule_id": "no-redundant-list-copy",
    "severity": "warning",
    "message": "The function step3_duplicate_list performs a redundant duplication operation that can be simplified.",
    "line": 11,
    "suggestion": "Replace with a more efficient list comprehension or direct duplication logic."
  },
  {
    "rule_id": "no-duplicate-code",
    "severity": "warning",
    "message": "Repeated pattern of appending elements in loops across multiple functions.",
    "line": 11,
    "suggestion": "Refactor repeated list-building logic into a reusable helper function."
  },
  {
    "rule_id": "no-side-effects-in-expressions",
    "severity": "error",
    "message": "Function step6_print_all has side effects (printing) inside a processing chain.",
    "line": 22,
    "suggestion": "Separate side-effect operations from pure data transformation logic."
  },
  {
    "rule_id": "no-unnecessary-string-concat",
    "severity": "info",
    "message": "String concatenation in step7_redundant_summary could be replaced with f-string or format.",
    "line": 29,
    "suggestion": "Use f\"Total items: {count}\" for better readability."
  }
]
```