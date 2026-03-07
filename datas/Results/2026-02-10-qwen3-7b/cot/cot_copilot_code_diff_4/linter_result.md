[
    {
        "rule_id": "no-underscore-in-constants",
        "severity": "error",
        "message": "Constant 'test.db' should use uppercase underscores for clarity.",
        "line": 3,
        "suggestion": "Rename to TEST_DB for consistency."
    },
    {
        "rule_id": "no-underscore-in-variables",
        "severity": "error",
        "message": "Variables 'conn' and 'cursorThing' should use descriptive names.",
        "line": 4,
        "suggestion": "Use 'db_connection' and 'cursor' for clarity."
    },
    {
        "rule_id": "no-underscore-in-parameters",
        "severity": "error",
        "message": "Function 'functionThatDoesTooManyThingsAndIsHardToRead()' lacks clear parameters.",
        "line": 6,
        "suggestion": "Add parameters for database connection and query logic."
    },
    {
        "rule_id": "no-underscore-in-exception-handling",
        "severity": "error",
        "message": "Exception handling lacks specificity and clarity.",
        "line": 15,
        "suggestion": "Catch specific exceptions and log meaningful messages."
    },
    {
        "rule_id": "no-underscore-in-print-statements",
        "severity": "warning",
        "message": "Print statements are not necessary for production code.",
        "line": 18,
        "suggestion": "Remove debug prints and replace with logging."
    },
    {
        "rule_id": "no-underscore-in-function-name",
        "severity": "error",
        "message": "Function name is too vague and lacks semantic meaning.",
        "line": 6,
        "suggestion": "Rename to 'initialize_database' or similar."
    },
    {
        "rule_id": "no-underscore-in-variables",
        "severity": "error",
        "message": "Variables 'name', 'age', 'anotherName', 'anotherAge' are not descriptive.",
        "line": 14,
        "suggestion": "Use 'user_name' and 'user_age' for clarity."
    },
    {
        "rule_id": "no-underscore-in-queries",
        "severity": "error",
        "message": "SQL queries lack parameterization and security.",
        "line": 17,
        "suggestion": "Use parameterized queries to prevent SQL injection."
    },
    {
        "rule_id": "no-underscore-in-exception-catch",
        "severity": "error",
        "message": "Exception handling lacks proper error classification.",
        "line": 21,
        "suggestion": "Catch specific exceptions and log errors with context."
    }
]