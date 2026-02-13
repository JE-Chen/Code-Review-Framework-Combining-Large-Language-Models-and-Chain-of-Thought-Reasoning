```json
[
    {
        "rule_id": "unused-variable",
        "severity": "warning",
        "message": "Variable 'anotherGlobal' is assigned but never used.",
        "line": 6,
        "suggestion": "Remove unused variable."
    },
    {
        "rule_id": "long-function-name",
        "severity": "warning",
        "message": "Function name 'veryStrangeFunctionNameThatDoesTooMuch' is too long and does not clearly describe its purpose.",
        "line": 8,
        "suggestion": "Rename to something more descriptive."
    },
    {
        "rule_id": "duplicate-code",
        "severity": "warning",
        "message": "The lambda functions connected to 'btn1' click event set the label text twice.",
        "line": 19,
        "suggestion": "Refactor to avoid duplicate code."
    },
    {
        "rule_id": "unnecessary-nesting",
        "severity": "warning",
        "message": "Nested functions 'inner' and 'inner2' are not needed.",
        "line": 26,
        "suggestion": "Simplify the code by removing unnecessary nesting."
    },
    {
        "rule_id": "magic-number",
        "severity": "info",
        "message": "Consider using named constants instead of magic numbers.",
        "line": 33,
        "suggestion": "Replace magic numbers with named constants."
    }
]
```