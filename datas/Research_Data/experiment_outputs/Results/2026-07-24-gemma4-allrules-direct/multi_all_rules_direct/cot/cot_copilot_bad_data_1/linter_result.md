```json
[
  {
    "rule_id": "no-mutable-default-argument",
    "severity": "error",
    "message": "Avoid using mutable default arguments (container=[]) in function definitions. This creates a shared state across all calls to the function.",
    "line": 1,
    "suggestion": "Use 'container=None' and initialize it as 'container = [] if container is None else container' inside the function."
  },
  {
    "rule_id": "no-shared-mutable-state",
    "severity": "warning",
    "message": "The use of a global mutable list 'shared_list' introduces hidden coupling and makes the code harder to test.",
    "line": 5,
    "suggestion": "Pass the list explicitly as an argument to the function."
  },
  {
    "rule_id": "no-input-mutation",
    "severity": "warning",
    "message": "The function 'mutate_input' modifies the input argument 'data' in place, which can lead to surprising side effects for the caller.",
    "line": 10,
    "suggestion": "Create a copy of the data or use a list comprehension to return a new list."
  },
  {
    "rule_id": "no-deeply-nested-conditionals",
    "severity": "warning",
    "message": "Deeply nested conditional logic increases cognitive load and reduces readability.",
    "line": 16,
    "suggestion": "Refactor using guard clauses or split the logic into smaller helper functions."
  },
  {
    "rule_id": "no-broad-exception",
    "severity": "error",
    "message": "Catching a broad exception 'except Exception:' can hide unexpected bugs and make debugging difficult.",
    "line": 33,
    "suggestion": "Catch specific exceptions, such as 'ZeroDivisionError' or 'TypeError'."
  },
  {
    "rule_id": "no-inconsistent-return-types",
    "severity": "warning",
    "message": "The function 'inconsistent_return' returns different types (int and str) depending on the condition.",
    "line": 37,
    "suggestion": "Ensure the function returns a consistent type or use a Union type hint and handle both cases at the call site."
  },
  {
    "rule_id": "no-invariant-in-loop",
    "severity": "info",
    "message": "The computation 'len(values)' is repeated inside the loop, which is inefficient.",
    "line": 43,
    "suggestion": "Calculate 'len(values)' once outside the loop and store it in a variable."
  },
  {
    "rule_id": "no-comprehension-side-effects",
    "severity": "warning",
    "message": "List comprehensions should be used for building collections, not for executing side effects like 'print()'.",
    "line": 47,
    "suggestion": "Use a standard 'for' loop for side effects."
  },
  {
    "rule_id": "no-magic-numbers",
    "severity": "info",
    "message": "The value '3.14159' is a magic number.",
    "line": 50,
    "suggestion": "Use 'math.pi' from the math module."
  },
  {
    "rule_id": "no-dynamic-execution",
    "severity": "error",
    "message": "The use of 'eval()' is a significant security risk as it can execute arbitrary code from external input.",
    "line": 53,
    "suggestion": "Avoid 'eval()'. Use a safer alternative like 'ast.literal_eval()' or a predefined mapping of allowed operations."
  }
]
```