[
  {
    "rule_id": "bad-naming",
    "severity": "warning",
    "message": "Variable 'cursorThing' is unclear and unprofessional.",
    "line": 4,
    "suggestion": "Rename to 'cursor' for clarity."
  },
  {
    "rule_id": "bad-naming",
    "severity": "warning",
    "message": "Function name 'functionThatDoesTooManyThingsAndIsHardToRead' is uninformative and describes the problem, not the behavior.",
    "line": 6,
    "suggestion": "Rename to a descriptive name reflecting the actual purpose, e.g., 'setup_database_and_insert_test_data'."
  },
  {
    "rule_id": "avoid-global",
    "severity": "warning",
    "message": "Global variables 'conn' and 'cursorThing' are used, complicating testing and maintenance.",
    "line": 7,
    "suggestion": "Avoid global state. Pass database connection and cursor as parameters."
  },
  {
    "rule_id": "ignore-exception",
    "severity": "warning",
    "message": "Exception caught but not handled or logged, making debugging difficult.",
    "line": 13,
    "suggestion": "Handle specific exceptions or re-raise with context."
  },
  {
    "rule_id": "sql-injection",
    "severity": "error",
    "message": "SQL query constructed with string concatenation, exposing to SQL injection.",
    "line": 18,
    "suggestion": "Use parameterized queries with cursor.execute(..., (param,))."
  },
  {
    "rule_id": "duplicate-code",
    "severity": "warning",
    "message": "Duplicate insert code pattern for Alice and Bob. Consider refactoring into a helper function.",
    "line": 18,
    "suggestion": "Extract insert logic into a helper function."
  },
  {
    "rule_id": "sql-injection",
    "severity": "error",
    "message": "SQL query constructed with string concatenation, exposing to SQL injection.",
    "line": 22,
    "suggestion": "Use parameterized queries with cursor.execute(..., (param,))."
  },
  {
    "rule_id": "sql-injection",
    "severity": "error",
    "message": "SQL query constructed with string concatenation, exposing to SQL injection.",
    "line": 25,
    "suggestion": "Use parameterized queries with cursor.execute(..., (param,))."
  },
  {
    "rule_id": "redundant-check",
    "severity": "warning",
    "message": "Redundant row length check; rows are expected to have content.",
    "line": 28,
    "suggestion": "Remove redundant length check."
  },
  {
    "rule_id": "magic-index",
    "severity": "warning",
    "message": "Using magic index 1 to access column data is error-prone and hard to maintain.",
    "line": 29,
    "suggestion": "Use named columns or document the column order."
  },
  {
    "rule_id": "magic-index",
    "severity": "warning",
    "message": "Using magic index 1 to access column data is error-prone and hard to maintain.",
    "line": 32,
    "suggestion": "Use named columns or document the column order."
  },
  {
    "rule_id": "ignore-exception",
    "severity": "warning",
    "message": "Exception caught but not handled or logged, making debugging difficult.",
    "line": 36,
    "suggestion": "Handle specific exceptions or re-raise with context."
  }
]