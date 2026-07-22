```json
[
    {
        "rule_id": "complex-logic",
        "severity": "warning",
        "message": "Function 'doSomething' has multiple levels of nested conditionals.",
        "line": 2,
        "suggestion": "Consider breaking down the function into smaller, more focused functions."
    },
    {
        "rule_id": "explicit-comparisons",
        "severity": "warning",
        "message": "Implicit comparison with None might not behave as expected.",
        "line": 24,
        "suggestion": "Replace 'f == None' with 'f is None'."
    },
    {
        "rule_id": "variable-naming",
        "severity": "info",
        "message": "Variable 'k' could be renamed for better clarity.",
        "line": 10,
        "suggestion": "Consider renaming to something like 'index'."
    },
    {
        "rule_id": "nested-if-statements",
        "severity": "warning",
        "message": "Nested if statements can reduce readability.",
        "line": 2,
        "suggestion": "Consider simplifying the logic or extracting some conditions into separate functions."
    }
]
```