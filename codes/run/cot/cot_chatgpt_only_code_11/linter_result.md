```json
[
    {
        "rule_id": "no-global-variables",
        "severity": "error",
        "message": "Global variables like USERS, USER_INDEX, MIXED_LOG, etc., should be avoided.",
        "line": 3,
        "suggestion": "Use classes or modules to encapsulate state."
    },
    {
        "rule_id": "function-length",
        "severity": "warning",
        "message": "Function 'find_users_by_age' has too many lines (19).",
        "line": 118,
        "suggestion": "Refactor into smaller functions."
    },
    {
        "rule_id": "function-length",
        "severity": "warning",
        "message": "Function 'analyze_users' has too many lines (16).",
        "line": 145,
        "suggestion": "Refactor into smaller functions."
    },
    {
        "rule_id": "variable-naming",
        "severity": "warning",
        "message": "Variable 'pos' could be more descriptive.",
        "line": 43,
        "suggestion": "Rename to 'user_index_pos'."
    },
    {
        "rule_id": "variable-naming",
        "severity": "warning",
        "message": "Variable 'i' is used as a loop variable but is also referenced outside the loop.",
        "line": 122,
        "suggestion": "Rename to avoid confusion."
    },
    {
        "rule_id": "comment-quality",
        "severity": "info",
        "message": "Comment at the top of each file is redundant.",
        "line": 1,
        "suggestion": "Remove or update comment."
    }
]
```