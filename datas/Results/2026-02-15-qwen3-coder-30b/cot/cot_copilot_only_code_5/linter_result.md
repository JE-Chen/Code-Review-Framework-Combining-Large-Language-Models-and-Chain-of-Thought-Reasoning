```json
[
  {
    "rule_id": "no-global-mutable-state",
    "severity": "error",
    "message": "Usage of global mutable state reduces testability and modularity.",
    "line": 1,
    "suggestion": "Pass state as parameters or use a class to encapsulate it."
  },
  {
    "rule_id": "no-inline-logic",
    "severity": "warning",
    "message": "Logic for processing items is tightly coupled and hard to test in isolation.",
    "line": 19,
    "suggestion": "Extract the conditional logic into a separate helper function."
  },
  {
    "rule_id": "no-hardcoded-values",
    "severity": "warning",
    "message": "Hardcoded threshold value may reduce flexibility and readability.",
    "line": 5,
    "suggestion": "Define threshold as a named constant or parameter."
  },
  {
    "rule_id": "no-duplicated-code",
    "severity": "warning",
    "message": "Repeated access to GLOBAL_STATE keys increases redundancy and error risk.",
    "line": 8,
    "suggestion": "Cache frequently accessed values from GLOBAL_STATE into local variables."
  },
  {
    "rule_id": "no-print-in-core",
    "severity": "warning",
    "message": "Direct printing inside core functions makes output harder to control and test.",
    "line": 33,
    "suggestion": "Return results instead of printing them; let calling code handle output."
  }
]
```