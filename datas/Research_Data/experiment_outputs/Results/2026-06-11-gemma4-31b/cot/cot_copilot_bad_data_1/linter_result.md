```json
[
  {
    "rule_id": "mutable-default-argument",
    "severity": "error",
    "message": "Function 'add_item' uses a mutable default argument (list). Default arguments are evaluated once at definition time, leading to shared state across calls.",
    "line": 1,
    "suggestion": "Set 'container=None' and initialize it as 'container = [] if container is None else container' inside the function."
  },
  {
    "rule_id": "shared-mutable-state",
    "severity": "warning",
    "message": "The use of the global variable 'shared_list' introduces hidden coupling and makes the code harder to test.",
    "line": 5,
    "suggestion": "Pass the list as an explicit argument to the 'append_global' function."
  },
  {
    "rule_id": "mutate-input-argument",
    "severity": "warning",
    "message": "Function 'mutate_input' modifies the input 'data' list in place without documentation stating this is intended.",
    "line": 10,
    "suggestion": "Create a copy of the list or use a list comprehension to return a new list."
  },
  {
    "rule_id": "complex-nesting",
    "severity": "info",
    "message": "Function 'nested_conditions' has deep nesting levels which reduces readability.",
    "line": 16,
    "suggestion": "Use guard clauses or a more flattened conditional structure to improve clarity."
  },
  {
    "rule_id": "broad-exception-handling",
    "severity": "warning",
    "message": "Function 'risky_division' catches the generic 'Exception' class, which may hide unexpected errors (e.g., KeyboardInterrupt).",
    "line": 36,
    "suggestion": "Catch specific exceptions, such as 'ZeroDivisionError' or 'TypeError'."
  },
  {
    "rule_id": "inconsistent-return-types",
    "severity": "error",
    "message": "Function 'inconsistent_return' returns different types (int and str) depending on the condition.",
    "line": 41,
    "suggestion": "Ensure the function returns a consistent type or use a Type Union if utilizing type hints."
  },
  {
    "rule_id": "invariant-in-loop",
    "severity": "warning",
    "message": "The expression 'len(values)' is computed repeatedly inside the loop in 'compute_in_loop'.",
    "line": 48,
    "suggestion": "Assign 'len(values)' to a variable outside the loop."
  },
  {
    "rule_id": "list-comprehension-side-effect",
    "severity": "error",
    "message": "List comprehension used for side effects (printing) rather than creating a collection.",
    "line": 53,
    "suggestion": "Use a standard 'for' loop for executing logic/side effects."
  },
  {
    "rule_id": "dynamic-code-execution",
    "severity": "error",
    "message": "Use of 'eval' in 'run_code' poses a severe security risk by allowing arbitrary code execution.",
    "line": 58,
    "suggestion": "Avoid 'eval'. Use a safer alternative like 'ast.literal_eval' or a dedicated parser."
  }
]
```