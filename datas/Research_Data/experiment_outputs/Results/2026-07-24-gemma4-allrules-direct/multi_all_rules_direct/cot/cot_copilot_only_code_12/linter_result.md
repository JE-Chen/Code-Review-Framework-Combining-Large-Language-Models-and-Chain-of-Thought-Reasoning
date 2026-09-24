```json
[
  {
    "rule_id": "shared-mutable-state",
    "severity": "error",
    "message": "Global mutable state (DATAFRAME, resultList, tempStorage) introduces hidden coupling and makes the code difficult to test and reason about.",
    "line": 6,
    "suggestion": "Encapsulate state within a class or pass data explicitly as function arguments and return values."
  },
  {
    "rule_id": "naming-conventions",
    "severity": "warning",
    "message": "Variable names 'resultList' and 'tempStorage' do not follow the standard Python snake_case convention.",
    "line": 7,
    "suggestion": "Rename to 'result_list' and 'temp_storage'."
  },
  {
    "rule_id": "naming-conventions",
    "severity": "warning",
    "message": "Function names 'loadData', 'calcStats', and 'plotData' do not follow the standard Python snake_case convention.",
    "line": 10,
    "suggestion": "Rename to 'load_data', 'calc_stats', and 'plot_data'."
  },
  {
    "rule_id": "deeply-nested-logic",
    "severity": "warning",
    "message": "Deeply nested conditional logic in 'calcStats' increases cognitive load.",
    "line": 21,
    "suggestion": "Use guard clauses or split the logic into smaller, focused functions for different column types."
  },
  {
    "rule_id": "unnecessary-work-in-loop",
    "severity": "warning",
    "message": "Repeated computation of 'st.mean(DATAFRAME[col])' inside the loop for column 'A'.",
    "line": 25,
    "suggestion": "Reuse the 'meanA' variable instead of recalculating the mean."
  },
  {
    "rule_id": "single-responsibility",
    "severity": "info",
    "message": "The 'calcStats' function is performing multiple responsibilities: calculating statistics, updating a global list, and updating a global dictionary.",
    "line": 19,
    "suggestion": "Separate the calculation logic from the state update logic."
  },
  {
    "rule_id": "magic-numbers",
    "severity": "info",
    "message": "Hard-coded constant '42' used in calculation without explanation.",
    "line": 30,
    "suggestion": "Define a named constant to explain the purpose of this value."
  }
]
```