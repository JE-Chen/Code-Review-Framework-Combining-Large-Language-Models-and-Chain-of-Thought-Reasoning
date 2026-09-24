```json
[
  {
    "rule_id": "deeply-nested-logic",
    "severity": "warning",
    "message": "Deeply nested conditional logic reduces readability and increases cognitive load.",
    "line": 31,
    "suggestion": "Use guard clauses to flatten the logic (e.g., if not s: print(...) continue)."
  },
  {
    "rule_id": "implicit-truthiness",
    "severity": "info",
    "message": "Avoid relying on implicit truthiness for complex objects or return values.",
    "line": 31,
    "suggestion": "Use an explicit comparison such as 'if len(s) != 0:' or 'if s != \"\":'."
  },
  {
    "rule_id": "unnecessary-work-in-loop",
    "severity": "info",
    "message": "The loop in step7_redundant_summary manually counts items, which is an unnecessary operation.",
    "line": 40,
    "suggestion": "Use the built-in len() function: return 'Total items: ' + str(len(strings))"
  }
]
```