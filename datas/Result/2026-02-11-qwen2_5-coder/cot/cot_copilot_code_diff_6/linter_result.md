```json
[
    {
        "rule_id": "global-variables",
        "severity": "warning",
        "message": "Global variables like GLOBAL_SESSION and ANOTHER_GLOBAL can lead to unexpected side effects and make the code harder to test.",
        "line": 4,
        "suggestion": "Consider passing dependencies through functions or using dependency injection."
    },
    {
        "rule_id": "print-statements",
        "severity": "error",
        "message": "Using print statements for debugging is discouraged in production code. Consider using logging instead.",
        "line": 8,
        "suggestion": "Replace `print` with `logging.info`, `logging.error`, etc."
    },
    {
        "rule_id": "except-except",
        "severity": "error",
        "message": "General exception handling (`except:`) without specifying the exception type catches all exceptions, including system-exiting exceptions.",
        "line": 19,
        "suggestion": "Catch specific exceptions or at least log them properly."
    },
    {
        "rule_id": "variable-naming",
        "severity": "warning",
        "message": "Variable name 'weirdVariableName' does not follow naming conventions.",
        "line": 25,
        "suggestion": "Use a more descriptive name that reflects the variable's purpose."
    }
]
```