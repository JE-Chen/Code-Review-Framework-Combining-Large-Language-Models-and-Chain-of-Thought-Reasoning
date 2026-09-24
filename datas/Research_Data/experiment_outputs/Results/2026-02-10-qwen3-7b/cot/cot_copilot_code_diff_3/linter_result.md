```python
linter_messages = [
    {
        "rule_id": "no-unused-vars",
        "severity": "error",
        "message": "Variables 'globalLabel' and 'anotherGlobal' are not used and should be removed.",
        "line": 12,
        "suggestion": "Remove unused variables and ensure all used variables are properly declared."
    },
    {
        "rule_id": "no-global-variables",
        "severity": "error",
        "message": "Global variables 'globalLabel' and 'anotherGlobal' are not used and should be avoided.",
        "line": 14,
        "suggestion": "Use local variables or pass them as parameters instead of relying on global scope."
    },
    {
        "rule_id": "no-nested-functions",
        "severity": "warning",
        "message": "Function 'inner' is nested inside 'veryStrangeFunctionNameThatDoesTooMuch' and should be refactored.",
        "line": 18,
        "suggestion": "Extract 'inner' into a separate helper function for better readability and maintainability."
    },
    {
        "rule_id": "no-redundant-events",
        "severity": "warning",
        "message": "Multiple 'clicked' event handlers are assigned to the same button, risking unexpected behavior.",
        "line": 21,
        "suggestion": "Use a single event handler with a lambda that performs both actions."
    },
    {
        "rule_id": "no-comment",
        "severity": "error",
        "message": "Missing documentation comments for critical functions and classes.",
        "line": 10,
        "suggestion": "Add docstrings explaining the purpose and behavior of the function and class."
    }
]
```