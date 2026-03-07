```json
[
  {
    "rule_id": "global-variables",
    "severity": "warning",
    "message": "Usage of global variables (USERS, USER_INDEX, MIXED_LOG) reduces modularity and testability.",
    "line": 3,
    "suggestion": "Encapsulate data within a class or pass state explicitly."
  },
  {
    "rule_id": "no-magic-numbers",
    "severity": "warning",
    "message": "Magic number '4' used as index for friends list in create_user_record.",
    "line": 8,
    "suggestion": "Define constants or use named indices for better readability."
  },
  {
    "rule_id": "no-magic-numbers",
    "severity": "warning",
    "message": "Magic number '2' used as index for age in user records.",
    "line": 35,
    "suggestion": "Use a named constant or field access instead."
  },
  {
    "rule_id": "no-duplicate-code",
    "severity": "warning",
    "message": "Duplicate logic in building age map and extracting unique ages.",
    "line": 42,
    "suggestion": "Refactor repeated operations into helper functions."
  },
  {
    "rule_id": "no-side-effects",
    "severity": "warning",
    "message": "Function 'remove_young_users' modifies global state directly.",
    "line": 53,
    "suggestion": "Avoid modifying shared mutable state in place."
  },
  {
    "rule_id": "no-side-effects",
    "severity": "warning",
    "message": "Function 'mark_inactive' mutates global user record.",
    "line": 64,
    "suggestion": "Return updated record rather than mutating in place."
  },
  {
    "rule_id": "no-loop-without-break",
    "severity": "warning",
    "message": "Inefficient linear search through FRIEND_A/FRIEND_B lists.",
    "line": 26,
    "suggestion": "Use hash-based lookup (e.g., dict) for O(1) retrieval."
  },
  {
    "rule_id": "no-unnecessary-operations",
    "severity": "warning",
    "message": "Unnecessary intermediate list creation when building age map.",
    "line": 44,
    "suggestion": "Simplify conversion using direct mapping."
  },
  {
    "rule_id": "no-inconsistent-naming",
    "severity": "warning",
    "message": "Variable naming inconsistency between snake_case and camelCase.",
    "line": 19,
    "suggestion": "Stick to one naming convention throughout."
  },
  {
    "rule_id": "no-unreachable-code",
    "severity": "warning",
    "message": "Code after 'return' statement may never execute.",
    "line": 23,
    "suggestion": "Ensure all paths are logically reachable."
  }
]
```