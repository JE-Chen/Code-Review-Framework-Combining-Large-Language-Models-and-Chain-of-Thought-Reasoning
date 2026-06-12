Based on the global rules provided, here is the code review conducted in the requested `linter_messages` format.

```json
[
  {
    "rule_id": "indentation-error",
    "severity": "error",
    "message": "The method 'process' in 'BaseProcessor' is not indented relative to the class definition.",
    "line": 2,
    "suggestion": "Indent the method body by 4 spaces."
  },
  {
    "rule_id": "performance-string-concatenation",
    "severity": "warning",
    "message": "Repeated string concatenation using '+=' inside a loop is inefficient in Python.",
    "line": 10,
    "suggestion": "Collect characters in a list and use ''.join(list) at the end."
  },
  {
    "rule_id": "naming-convention-generic",
    "severity": "info",
    "message": "Variable name 'ch' is overly concise.",
    "line": 9,
    "suggestion": "Rename 'ch' to 'char' or 'character' for better readability."
  },
  {
    "rule_id": "complexity-nested-conditionals",
    "severity": "warning",
    "message": "Deeply nested if-statements (arrow code) reduce maintainability and readability.",
    "line": 48,
    "suggestion": "Use guard clauses (early returns) or combine conditions to flatten the structure."
  },
  {
    "rule_id": "software-engineering-modularity",
    "severity": "info",
    "message": "The 'GLOBAL_CONFIG' dictionary is defined in the global scope, which can lead to side-effect issues in larger systems.",
    "line": 34,
    "suggestion": "Encapsulate configuration in a class or a dedicated config module/provider."
  },
  {
    "rule_id": "documentation-missing",
    "severity": "info",
    "message": "Classes and public methods lack docstrings explaining their purpose and expected types.",
    "line": 1,
    "suggestion": "Add PEP 257 compliant docstrings to classes and methods."
  },
  {
    "rule_id": "testing-missing",
    "severity": "warning",
    "message": "No unit tests are provided to verify the logic of processors or the pipeline.",
    "line": 0,
    "suggestion": "Implement unit tests using pytest or unittest to cover edge cases (e.g., empty strings, non-int/str types)."
  }
]
```