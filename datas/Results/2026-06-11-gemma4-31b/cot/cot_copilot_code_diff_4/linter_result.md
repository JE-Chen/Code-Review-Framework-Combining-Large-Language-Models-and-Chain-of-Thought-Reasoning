Based on the provided global rules, here is the code review and the structured linter messages.

### Overall Review
The provided code violates several fundamental software engineering principles. It suffers from poor naming conventions, significant security vulnerabilities (SQL Injection), poor error handling, and a lack of modularity. The use of global state for database connections is a major anti-pattern that will prevent the code from being scalable or testable.

---

### Linter Messages

```json
[
  {
    "rule_id": "global-state-usage",
    "severity": "error",
    "message": "Use of global variables 'conn' and 'cursorThing' creates hidden dependencies and makes the code non-thread-safe.",
    "line": 3,
    "suggestion": "Pass the connection/cursor as arguments to functions or encapsulate them in a class."
  },
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Function name 'functionThatDoesTooManyThingsAndIsHardToRead' is too verbose and does not describe the business purpose.",
    "line": 6,
    "suggestion": "Rename to something descriptive like 'initialize_and_populate_users'."
  },
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Variable 'cursorThing' does not follow PEP 8 naming conventions and is not descriptive.",
    "line": 4,
    "suggestion": "Rename to 'cursor'."
  },
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Variable 'anotherName' uses camelCase, which is inconsistent with Python's snake_case convention.",
    "line": 18,
    "suggestion": "Rename to 'another_name'."
  },
  {
    "rule_id": "sql-injection",
    "severity": "error",
    "message": "Directly interpolating variables into SQL queries allows for SQL Injection attacks.",
    "line": 15,
    "suggestion": "Use parameterized queries: cursor.execute('INSERT INTO users(name, age) VALUES(?, ?)', (name, age))"
  },
  {
    "rule_id": "sql-injection",
    "severity": "error",
    "message": "Directly interpolating variables into SQL queries allows for SQL Injection attacks.",
    "line": 20,
    "suggestion": "Use parameterized queries: cursor.execute('INSERT INTO users(name, age) VALUES(?, ?)', (another_name, another_age))"
  },
  {
    "rule_id": "broad-exception",
    "severity": "warning",
    "message": "Bare 'except:' clause catches all exceptions, including SystemExit and KeyboardInterrupt, masking potential bugs.",
    "line": 28,
    "suggestion": "Specify the exception type, e.g., 'except sqlite3.Error:'."
  },
  {
    "rule_id": "complexity",
    "severity": "info",
    "message": "Deeply nested if-else blocks reduce readability.",
    "line": 24,
    "suggestion": "Use elif statements or a mapping dictionary to handle different user names."
  },
  {
    "rule_id": "modularization",
    "severity": "warning",
    "message": "Function performs multiple unrelated tasks: connection management, schema creation, data insertion, and data retrieval.",
    "line": 6,
    "suggestion": "Split into separate functions: 'create_db', 'insert_user', and 'query_users'."
  },
  {
    "rule_id": "resource-management",
    "severity": "warning",
    "message": "Database connection is closed at the end of the function but not in a 'finally' block, risking leaks if an exception occurs.",
    "line": 31,
    "suggestion": "Use a 'with' statement (context manager) for the connection."
  }
]
```