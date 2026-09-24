```json
[
  {
    "rule_id": "mutable-default-argument",
    "severity": "error",
    "message": "Avoid using mutable default arguments (like lists) in function definitions. They are evaluated once at definition time and shared across calls.",
    "line": 1,
    "suggestion": "Use 'container=None' and initialize it inside the function: 'if container is None: container = []'"
  },
  {
    "rule_id": "shared-mutable-state",
    "severity": "warning",
    "message": "Use of shared mutable state at the module level ('shared_list') can introduce hidden coupling and make testing difficult.",
    "line": 5,
    "suggestion": "Pass the state explicitly as an argument to the function."
  },
  {
    "rule_id": "mutate-input-argument",
    "severity": "warning",
    "message": "The function modifies its input argument 'data' in place, which can lead to surprising side effects for the caller.",
    "line": 10,
    "suggestion": "Create a copy of the data or return a new list using a list comprehension."
  },
  {
    "rule_id": "deeply-nested-conditionals",
    "severity": "warning",
    "message": "Deeply nested conditional logic increases cognitive load and reduces readability.",
    "line": 16,
    "suggestion": "Refactor using guard clauses or split the logic into smaller, focused functions."
  },
  {
    "rule_id": "inconsistent-return-types",
    "severity": "error",
    "message": "The function returns different types (int and str) depending on the condition, which increases the burden on the caller.",
    "line": 36,
    "suggestion": "Ensure the function returns a consistent type, or use a Union type if strictly necessary and documented."
  },
  {
    "rule_id": "unnecessary-work-in-loop",
    "severity": "info",
    "message": "The computation 'len(values)' is repeated inside the loop; it is an invariant that can be moved outside.",
    "line": 42,
    "suggestion": "Assign 'limit = len(values)' before the loop starts."
  },
  {
    "rule_id": "comprehension-for-side-effects",
    "severity": "error",
    "message": "List comprehensions should be used for building collections, not for executing logic with side effects (like print).",
    "line": 46,
    "suggestion": "Use an explicit 'for' loop."
  },
  {
    "rule_id": "magic-number",
    "severity": "info",
    "message": "Hard-coded constant '3.14159' used for Pi.",
    "line": 49,
    "suggestion": "Use 'math.pi' from the standard library."
  },
  {
    "rule_id": "dynamic-code-execution",
    "severity": "error",
    "message": "Use of 'eval' introduces serious security risks and makes the code harder to reason about.",
    "line": 52,
    "suggestion": "Avoid 'eval'; use a safer alternative like 'ast.literal_eval' or a predefined mapping of allowed operations."
  }
]
```