```json
[
  {
    "rule_id": "global-state-mutation",
    "severity": "error",
    "message": "Global state is mutated in multiple places, leading to unclear dependencies and hard-to-test logic.",
    "line": 14,
    "suggestion": "Refactor to use instance variables or pass state explicitly."
  },
  {
    "rule_id": "blocking-operation-in-ui",
    "severity": "error",
    "message": "time.sleep() is used in UI event handler, which blocks the main thread and causes poor responsiveness.",
    "line": 32,
    "suggestion": "Use non-blocking alternatives like QTimer.singleShot or async patterns."
  },
  {
    "rule_id": "magic-number",
    "severity": "warning",
    "message": "Magic number '777' used as timer interval without explanation.",
    "line": 41,
    "suggestion": "Define as a named constant with descriptive name."
  },
  {
    "rule_id": "magic-string",
    "severity": "warning",
    "message": "String literals like 'Click maybe', 'Don't click', etc., are repeated without constants.",
    "line": 48,
    "suggestion": "Extract into a shared list or constant for reuse and maintainability."
  },
  {
    "rule_id": "inconsistent-naming",
    "severity": "warning",
    "message": "Variable naming is inconsistent; some are snake_case while others are camelCase.",
    "line": 10,
    "suggestion": "Stick to snake_case for consistency across the project."
  },
  {
    "rule_id": "hardcoded-values",
    "severity": "warning",
    "message": "Hardcoded values such as '300', '200', and '777' should be configurable.",
    "line": 29,
    "suggestion": "Move these values into configuration or constants."
  },
  {
    "rule_id": "duplicate-logic",
    "severity": "warning",
    "message": "The same pattern of accessing GLOBAL_THING is repeated in several methods.",
    "line": 20,
    "suggestion": "Consider encapsulating access to GLOBAL_THING behind a getter/setter."
  }
]
```