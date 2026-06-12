```json
[
  {
    "rule_id": "naming-conventions",
    "severity": "warning",
    "message": "Function name 'doSomething' uses camelCase; Python convention (PEP 8) prescribes snake_case.",
    "line": 1,
    "suggestion": "Rename to 'do_something'."
  },
  {
    "rule_id": "descriptive-naming",
    "severity": "error",
    "message": "Function parameters 'a' through 'j' are non-descriptive and provide no semantic meaning.",
    "line": 1,
    "suggestion": "Rename parameters to reflect their actual purpose and intent."
  },
  {
    "rule_id": "deeply-nested-logic",
    "severity": "error",
    "message": "Deeply nested conditional logic increases cognitive load and reduces readability.",
    "line": 3,
    "suggestion": "Refactor using guard clauses (early returns) to flatten the structure."
  },
  {
    "rule_id": "naming-conventions",
    "severity": "warning",
    "message": "Variable name 'dataList' uses camelCase; Python convention prescribes snake_case.",
    "line": 22,
    "suggestion": "Rename to 'data_list'."
  },
  {
    "rule_id": "shared-mutable-state",
    "severity": "warning",
    "message": "Variable 'dataList' is defined at the module level and accessed globally inside 'processData'.",
    "line": 22,
    "suggestion": "Pass the list as an explicit argument to the 'processData' function."
  },
  {
    "rule_id": "unnecessary-work-in-loops",
    "severity": "info",
    "message": "Using 'range(len(dataList))' to index a list is less efficient and less readable than direct iteration.",
    "line": 26,
    "suggestion": "Use 'for item in dataList:'."
  },
  {
    "rule_id": "deeply-nested-logic",
    "severity": "warning",
    "message": "Nested conditionals used for value range checking are difficult to follow.",
    "line": 36,
    "suggestion": "Use 'if/elif/else' blocks to handle range boundaries linearly."
  },
  {
    "rule_id": "function-responsibility",
    "severity": "info",
    "message": "The 'main' function is performing multiple unrelated tasks (testing 'doSomething', 'processData', and manual range printing).",
    "line": 32,
    "suggestion": "Split the logic into smaller, focused helper functions."
  }
]
```