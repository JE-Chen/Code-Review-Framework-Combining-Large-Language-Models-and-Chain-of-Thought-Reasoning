```json
[
  {
    "rule_id": "no-global-assign",
    "severity": "error",
    "message": "Assignment to global variable 'total_result' violates encapsulation and makes state management unclear.",
    "line": 10,
    "suggestion": "Pass 'total_result' as a parameter or use a class to manage state."
  },
  {
    "rule_id": "no-magic-numbers",
    "severity": "warning",
    "message": "Magic number 3.14159 used for π; consider defining it as a named constant.",
    "line": 6,
    "suggestion": "Define PI = 3.14159 and use it consistently."
  },
  {
    "rule_id": "no-magic-numbers",
    "severity": "warning",
    "message": "Magic number 2.71828 used for e; consider defining it as a named constant.",
    "line": 8,
    "suggestion": "Define E = 2.71828 and use it consistently."
  },
  {
    "rule_id": "no-duplicate-key",
    "severity": "error",
    "message": "Duplicate key 'flag1', 'flag2', etc. in function call to 'doStuff'; this may indicate confusion or redundancy.",
    "line": 48,
    "suggestion": "Ensure all arguments are unique and meaningful, or refactor into a config object."
  },
  {
    "rule_id": "no-unused-vars",
    "severity": "warning",
    "message": "Unused variable 'temp1' and 'temp2' in function 'doStuff'.",
    "line": 23,
    "suggestion": "Remove unused variables or explain their purpose."
  },
  {
    "rule_id": "no-implicit-bool",
    "severity": "warning",
    "message": "Implicit boolean check on 'i or j' might mask unexpected behavior; prefer explicit checks.",
    "line": 28,
    "suggestion": "Use explicit conditional logic such as 'if i is not None or j is not None'."
  },
  {
    "rule_id": "no-implicit-any",
    "severity": "warning",
    "message": "Catch-all exception in 'processEverything' hides potential issues; handle specific exceptions.",
    "line": 36,
    "suggestion": "Catch specific exceptions like ValueError instead of broad except clause."
  },
  {
    "rule_id": "no-unsafe-default-arg",
    "severity": "error",
    "message": "Mutable default argument 'bucket=[]' in 'collectValues' leads to shared state across calls.",
    "line": 52,
    "suggestion": "Use None as default and initialize inside function body: 'bucket = bucket or []'."
  },
  {
    "rule_id": "no-nested-conditionals",
    "severity": "warning",
    "message": "Deep nesting in conditional blocks reduces readability; consider extracting logic.",
    "line": 13,
    "suggestion": "Refactor nested conditionals using early returns or helper functions."
  },
  {
    "rule_id": "no-side-effects-in-loop",
    "severity": "warning",
    "message": "Side effect via 'time.sleep(0.01)' inside loop could slow down execution unnecessarily.",
    "line": 25,
    "suggestion": "Move timing logic outside critical paths or abstract into a separate utility."
  },
  {
    "rule_id": "no-duplicated-code",
    "severity": "warning",
    "message": "Repeated assignment patterns in processing logic suggest possible refactoring opportunity.",
    "line": 31,
    "suggestion": "Extract reusable logic into helper functions."
  }
]
```