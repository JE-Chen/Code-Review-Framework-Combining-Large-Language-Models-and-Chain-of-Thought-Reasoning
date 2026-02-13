[
    {
        "rule_id": "global-variable-usage",
        "severity": "error",
        "message": "Global variables GLOBAL_DATA_THING and GLOBAL_FLAG are not encapsulated in classes or passed as parameters. They introduce coupling and reduce testability.",
        "line": 15,
        "suggestion": "Encapsulate global state in a class or pass dependencies explicitly."
    },
    {
        "rule_id": "unused-variable",
        "severity": "warning",
        "message": "Variable 'self.weird_counter' is used but not needed in the logic flow.",
        "line": 42,
        "suggestion": "Remove or rename the variable for clarity."
    },
    {
        "rule_id": "method-naming",
        "severity": "warning",
        "message": "Method 'make_data_somehow' lacks descriptive naming and is not clear about its purpose.",
        "line": 31,
        "suggestion": "Rename to something like 'generate_data' or 'initialize_data'."
    },
    {
        "rule_id": "lambda-usage",
        "severity": "warning",
        "message": "Lambda function in 'analyze_in_a_hurry' is not well-structured and may be harder to read.",
        "line": 47,
        "suggestion": "Break the lambda into multiple lines or use a helper function."
    },
    {
        "rule_id": "math-function-usage",
        "severity": "warning",
        "message": "Random.gauss() is used without clear justification. Consider replacing with more appropriate functions.",
        "line": 48,
        "suggestion": "Use numpy.random.Generator for controlled randomness."
    },
    {
        "rule_id": "missing-comments",
        "severity": "warning",
        "message": "Many methods lack explanatory comments, reducing readability and maintainability.",
        "line": 35,
        "suggestion": "Add inline comments explaining the purpose and logic of each method."
    },
    {
        "rule_id": "logical-bug",
        "severity": "error",
        "message": "The 'mix' column calculation in 'analyze_in_a_hurry' may have logical errors or inefficiencies.",
        "line": 47,
        "suggestion": "Refactor the 'mix' calculation to ensure correctness and performance."
    },
    {
        "rule_id": "performance-bottleneck",
        "severity": "warning",
        "message": "Time.sleep() is used in multiple methods, which is inefficient and not recommended.",
        "line": 37,
        "suggestion": "Replace with async or other non-blocking mechanisms."
    }
]