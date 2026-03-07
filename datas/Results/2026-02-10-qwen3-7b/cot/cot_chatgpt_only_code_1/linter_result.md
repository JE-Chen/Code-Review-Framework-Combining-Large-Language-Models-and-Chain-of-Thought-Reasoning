[
    {
        "rule_id": "global-variable-usage",
        "severity": "error",
        "message": "Global variable `total_result` is used in `doStuff` but not declared or used in the function.",
        "line": 10,
        "suggestion": "Avoid global variables. Use a class or pass `total_result` as a parameter."
    },
    {
        "rule_id": "unused-variable",
        "severity": "warning",
        "message": "Variable `z` is unused in `doStuff`.",
        "line": 11,
        "suggestion": "Remove or re-use `z` for clarity."
    },
    {
        "rule_id": "redundant-conditions",
        "severity": "error",
        "message": "Too many nested conditions in `doStuff` (e.g., `if g: if h: ...`).",
        "line": 12,
        "suggestion": "Simplify logic and extract helper functions for readability."
    },
    {
        "rule_id": "unnecessary-imports",
        "severity": "warning",
        "message": "Imports `math` and `time` are unused in the code.",
        "line": 1,
        "suggestion": "Remove unused imports for cleaner code."
    },
    {
        "rule_id": "redundant-calls",
        "severity": "warning",
        "message": "Redundant `collectValues` calls in `main`.",
        "line": 15,
        "suggestion": "Remove or use `collectValues` only where needed."
    },
    {
        "rule_id": "unnecessary-prints",
        "severity": "warning",
        "message": "Print statements in `main` are not needed.",
        "line": 17,
        "suggestion": "Remove or replace with logic."
    },
    {
        "rule_id": "global-variable-usage",
        "severity": "error",
        "message": "Global variable `total_result` is used in `doStuff` but not declared in the function.",
        "line": 10,
        "suggestion": "Avoid global variables. Pass `total_result` as a parameter."
    }
]