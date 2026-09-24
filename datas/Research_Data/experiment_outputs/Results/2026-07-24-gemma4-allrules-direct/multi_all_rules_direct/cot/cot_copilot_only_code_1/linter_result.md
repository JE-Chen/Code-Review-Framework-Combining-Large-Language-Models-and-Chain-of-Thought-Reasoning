```json
[
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Function name 'doSomething' does not follow PEP 8 naming conventions (should be snake_case).",
    "line": 1,
    "suggestion": "Rename to 'do_something'."
  },
  {
    "rule_id": "descriptive-naming",
    "severity": "warning",
    "message": "Function parameters 'a' through 'j' are not descriptive and provide no semantic meaning.",
    "line": 1,
    "suggestion": "Use meaningful names that describe the purpose of each argument."
  },
  {
    "rule_id": "deeply-nested-logic",
    "severity": "error",
    "message": "Deeply nested conditional logic increases cognitive load and reduces readability.",
    "line": 3,
    "suggestion": "Refactor using guard clauses or split the logic into smaller, focused functions."
  },
  {
    "rule_id": "magic-number",
    "severity": "info",
    "message": "Use of magic numbers (e.g., 999999, 1234, 42, 123456789) without explanation.",
    "line": 7,
    "suggestion": "Define these values as named constants at the top of the module."
  },
  {
    "rule_id": "shared-mutable-state",
    "severity": "warning",
    "message": "The variable 'dataList' is a global mutable list, which can introduce hidden coupling.",
    "line": 21,
    "suggestion": "Pass the list as an explicit argument to 'processData'."
  },
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Variable name 'dataList' does not follow PEP 8 naming conventions (should be snake_case).",
    "line": 21,
    "suggestion": "Rename to 'data_list'."
  },
  {
    "rule_id": "unnecessary-work-in-loop",
    "severity": "info",
    "message": "Using 'range(len(dataList))' to iterate over a list is less efficient and less Pythonic than direct iteration.",
    "line": 25,
    "suggestion": "Use 'for item in dataList:'."
  },
  {
    "rule_id": "deeply-nested-logic",
    "severity": "error",
    "message": "Deeply nested conditional logic used for value checking.",
    "line": 36,
    "suggestion": "Use 'elif' statements or a mapping to flatten the control flow."
  }
]
```