```json
[
  {
    "rule_id": "implicit-truthiness",
    "severity": "warning",
    "message": "Avoid relying on implicit truthiness for complex objects or return values. Use explicit comparisons for clarity.",
    "line": 32,
    "suggestion": "Change 'if len(text) > 0:' to 'if text:' or keep as is, but be consistent. More importantly, line 38 'if text:' should be 'if text != \"\":' or 'if len(text) > 0:'."
  },
  {
    "rule_id": "deeply-nested-conditionals",
    "severity": "warning",
    "message": "Deeply nested conditional logic reduces readability and increases cognitive load.",
    "line": 40,
    "suggestion": "Refactor the nested if-else chain into a series of guard clauses or a mapping/lookup table to flatten the structure."
  },
  {
    "rule_id": "implicit-truthiness",
    "severity": "warning",
    "message": "Avoid relying on implicit truthiness for strings when checking for content.",
    "line": 38,
    "suggestion": "Use 'if text != \"\":' or 'if len(text) > 0:' for explicit intent."
  }
]
```