```json
[
  {
    "rule_id": "mutable-default-argument",
    "severity": "error",
    "message": "Function 'add_item' uses a mutable default argument 'container=[]'. Default arguments are evaluated once at definition time, leading to shared state across calls.",
    "line": 1,
    "suggestion": "Use 'container=None' and initialize it inside the function: 'if container is None: container = []'."
  },
  {
    "rule_id": "shared-mutable-state",
    "severity": "warning",
    "message": "Function 'append_global' modifies a shared mutable state 'shared_list' at the module level, which can introduce hidden coupling.",
    "line": 7,
    "suggestion": "Pass the list as an explicit argument to the function."
  },
  {
    "rule_id": "mutate-input-argument",
    "severity": "warning",
    "message": "Function 'mutate_input' modifies the input argument 'data' in place without documentation.",
    "line": 11,
    "suggestion": "Create a copy of the data or return a new list to avoid side effects for the caller."
  },
  {
    "rule_id": "deeply-nested-conditionals",
    "severity": "warning",
    "message": "Function 'nested_conditions' contains deeply nested conditional logic, increasing cognitive load.",
    "line": 16,
    "suggestion": "Refactor using guard clauses or split the logic into smaller helper functions."
  },
  {
    "rule_id": "inconsistent-return-types",
    "severity": "error",
    "message": "Function 'inconsistent_return' returns different types (int and str) depending on the condition.",
    "line": 36,
    "suggestion": "Ensure the function returns a consistent type or use a Union type hint and handle it explicitly."
  },
  {
    "rule_id": "unnecessary-work-in-loop",
    "severity": "info",
    "message": "The expression 'len(values)' is evaluated in every iteration of the loop in 'compute_in_loop'.",
    "line": 42,
    "suggestion": "Move 'len(values)' to a variable outside the loop."
  },
  {
    "rule_id": "comprehension-side-effects",
    "severity": "error",
    "message": "List comprehension used for side effects (print) instead of building a collection.",
    "line": 46,
    "suggestion": "Use an explicit 'for' loop."
  },
  {
    "rule_id": "magic-number",
    "severity": "info",
    "message": "Hard-coded constant '3.14159' used in 'calculate_area'.",
    "line": 49,
    "suggestion": "Use 'math.pi' from the math module."
  },
  {
    "rule_id": "dynamic-code-execution",
    "severity": "error",
    "message": "Use of 'eval' in 'run_code' poses a significant security risk and makes the code harder to reason about.",
    "line": 52,
    "suggestion": "Avoid 'eval'; use a safer alternative like 'ast.literal_eval' or a predefined mapping of allowed operations."
  }
]
```