```json
[
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Function name 'doStuff' is not descriptive and does not follow PEP 8 (snake_case).",
    "line": 6,
    "suggestion": "Rename to a descriptive name like 'calculate_geometry_value'."
  },
  {
    "rule_id": "function-signature-complexity",
    "severity": "error",
    "message": "Function 'doStuff' has too many parameters (10), making it difficult to maintain and test.",
    "line": 6,
    "suggestion": "Group related parameters into a data class or dictionary."
  },
  {
    "rule_id": "deeply-nested-logic",
    "severity": "warning",
    "message": "Deeply nested if-statements reduce readability and increase cognitive load.",
    "line": 18,
    "suggestion": "Use guard clauses or a mapping strategy to flatten the logic."
  },
  {
    "rule_id": "shared-mutable-state",
    "severity": "error",
    "message": "Use of 'global total_result' introduces hidden coupling and makes the function non-deterministic/hard to test.",
    "line": 36,
    "suggestion": "Pass the accumulator as an argument or return the value to be summed by the caller."
  },
  {
    "rule_id": "performance-bottleneck",
    "severity": "warning",
    "message": "time.sleep(0.01) inside a function called within a loop introduces artificial latency.",
    "line": 39,
    "suggestion": "Remove the sleep call unless it is specifically required for rate-limiting."
  },
  {
    "rule_id": "implicit-truthiness",
    "severity": "warning",
    "message": "Checking 'if i or j' relies on implicit truthiness. Be explicit about what constitutes a valid state.",
    "line": 41,
    "suggestion": "Use explicit comparisons (e.g., 'if i is not None or j is not None')."
  },
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Function name 'processEverything' does not follow PEP 8 (snake_case).",
    "line": 47,
    "suggestion": "Rename to 'process_data_collection'."
  },
  {
    "rule_id": "type-checking-anti-pattern",
    "severity": "info",
    "message": "Using 'type(item) == int' is less flexible than 'isinstance()'.",
    "line": 51,
    "suggestion": "Use 'isinstance(item, int)'."
  },
  {
    "rule_id": "bare-except",
    "severity": "error",
    "message": "Bare 'except:' clause catches all exceptions, including SystemExit and KeyboardInterrupt.",
    "line": 57,
    "suggestion": "Catch specific exceptions, e.g., 'except ValueError:'."
  },
  {
    "rule_id": "shadowing-built-in",
    "severity": "warning",
    "message": "Variable 'sum' shadows the built-in Python function 'sum()'.",
    "line": 83,
    "suggestion": "Rename the variable to 'total_sum' or similar."
  },
  {
    "rule_id": "inefficient-conversion",
    "severity": "info",
    "message": "Converting a number to string and then back to float is unnecessary and inefficient.",
    "line": 85,
    "suggestion": "Use 'float(sum)' directly."
  },
  {
    "rule_id": "mutable-default-argument",
    "severity": "error",
    "message": "Using a mutable default argument 'bucket=[]' leads to shared state across all function calls.",
    "line": 89,
    "suggestion": "Set default to 'None' and initialize inside the function: 'if bucket is None: bucket = []'."
  },
  {
    "rule_id": "single-responsibility",
    "severity": "warning",
    "message": " 'processEverything' handles data cleaning, business logic, and aggregation in one block.",
    "line": 47,
    "suggestion": "Split into 'clean_data', 'calculate_results', and 'aggregate_results'."
  }
]
```