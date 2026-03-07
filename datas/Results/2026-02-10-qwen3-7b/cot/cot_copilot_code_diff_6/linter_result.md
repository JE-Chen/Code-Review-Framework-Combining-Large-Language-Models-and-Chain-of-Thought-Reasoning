```json
[
  {
    "rule_id": "no-unnecessary-try-except",
    "severity": "error",
    "message": "Repeated try-except blocks for error handling without proper logging or handling.",
    "line": 12,
    "suggestion": "Add logging for exceptions and ensure proper error handling."
  },
  {
    "rule_id": "no-global-variable-usage",
    "severity": "error",
    "message": "Global variables (GLOBAL_SESSION) are used without proper encapsulation or scope management.",
    "line": 5,
    "suggestion": "Avoid global variables and use local state or context managers."
  },
  {
    "rule_id": "no-descriptive-function-names",
    "severity": "error",
    "message": "Function name 'functionThatDoesTooMuchAndIsHardToUnderstand' lacks clarity and is not semantically meaningful.",
    "line": 10,
    "suggestion": "Rename to something like 'processBadRequests' or 'handleRequests'."
  },
  {
    "rule_id": "no-exception-specific-handling",
    "severity": "error",
    "message": "Exception handling lacks specificity and does not provide meaningful feedback.",
    "line": 17,
    "suggestion": "Log exceptions with contextual details and consider raising specific exceptions."
  },
  {
    "rule_id": "no-conditional-logic",
    "severity": "error",
    "message": "Conditional logic (e.g., 'if r2.status_code == 200') lacks clear intent and is not well-documented.",
    "line": 20,
    "suggestion": "Add comments explaining the purpose of the condition and consider refactoring."
  },
  {
    "rule_id": "no-exception-logging",
    "severity": "error",
    "message": "No logging or error tracking is implemented for failed requests.",
    "line": 23,
    "suggestion": "Add logging for all request failures and consider using a logging library."
  },
  {
    "rule_id": "no-logical-structure",
    "severity": "error",
    "message": "Code structure lacks clear separation of concerns and logical grouping of functionality.",
    "line": 14,
    "suggestion": "Refactor into smaller, well-defined functions with clear responsibilities."
  }
]
```