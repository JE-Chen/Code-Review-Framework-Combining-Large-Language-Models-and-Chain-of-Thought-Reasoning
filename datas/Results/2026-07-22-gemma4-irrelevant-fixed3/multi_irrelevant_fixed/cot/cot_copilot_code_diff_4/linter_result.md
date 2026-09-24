```json
[
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Variable 'cursorThing' does not follow snake_case naming convention and is not descriptive.",
    "line": 5,
    "suggestion": "Rename to 'cursor'."
  },
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Function name 'functionThatDoesTooManyThingsAndIsHardToRead' is overly verbose and does not follow snake_case convention.",
    "line": 7,
    "suggestion": "Rename to a concise, descriptive name like 'setup_and_query_users'."
  },
  {
    "rule_id": "software-engineering-standards",
    "severity": "error",
    "message": "Function violates the Single Responsibility Principle by handling connection, table creation, data insertion, and querying in one block.",
    "line": 7,
    "suggestion": "Split the function into smaller, modular functions (e.g., 'init_db', 'add_user', 'fetch_users')."
  },
  {
    "rule_id": "security-sql-injection",
    "severity": "error",
    "message": "SQL query constructed using string concatenation is vulnerable to SQL injection.",
    "line": 17,
    "suggestion": "Use parameterized queries: cursor.execute('INSERT INTO users(name, age) VALUES(?, ?)', (name, age))."
  },
  {
    "rule_id": "security-sql-injection",
    "severity": "error",
    "message": "SQL query constructed using string concatenation is vulnerable to SQL injection.",
    "line": 21,
    "suggestion": "Use parameterized queries: cursor.execute('INSERT INTO users(name, age) VALUES(?, ?)', (anotherName, anotherAge))."
  },
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Variable 'anotherName' and 'anotherAge' use camelCase instead of snake_case.",
    "line": 20,
    "suggestion": "Rename to 'another_name' and 'another_age'."
  },
  {
    "rule_id": "logic-correctness",
    "severity": "warning",
    "message": "Deeply nested if-else structure reduces readability.",
    "line": 28,
    "suggestion": "Use 'elif' statements to flatten the logic."
  },
  {
    "rule_id": "logic-correctness",
    "severity": "error",
    "message": "Bare 'except' clause catches all exceptions, including SystemExit and KeyboardInterrupt, which is bad practice.",
    "line": 35,
    "suggestion": "Catch specific exceptions (e.g., sqlite3.Error)."
  }
]
```