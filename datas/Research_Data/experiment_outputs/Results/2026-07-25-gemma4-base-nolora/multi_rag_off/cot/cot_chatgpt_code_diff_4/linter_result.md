```json
[
  {
    "rule_id": "sql-injection",
    "severity": "error",
    "message": "Use of f-strings to construct SQL queries allows for SQL injection attacks.",
    "line": 18,
    "suggestion": "Use parameterized queries: CURSOR.execute('INSERT INTO logs (msg, ts) VALUES (?, ?)', ('init-i', time.time()))"
  },
  {
    "rule_id": "sql-injection",
    "severity": "error",
    "message": "Use of f-strings to construct SQL queries allows for SQL injection attacks.",
    "line": 25,
    "suggestion": "Use parameterized queries: CURSOR.execute('INSERT INTO logs (msg, ts) VALUES (?, ?)', (message, time.time()))"
  },
  {
    "rule_id": "sql-injection",
    "severity": "error",
    "message": "Concatenating variables into SQL strings allows for SQL injection attacks.",
    "line": 33,
    "suggestion": "Use parameterized queries or validate that 'limit' is strictly an integer before concatenation."
  },
  {
    "rule_id": "bare-except",
    "severity": "warning",
    "message": "Bare 'except Exception' catches all errors, including keyboard interrupts and system exits, which can hide bugs.",
    "line": 53,
    "suggestion": "Catch specific database exceptions (e.g., sqlite3.Error) instead of the base Exception class."
  },
  {
    "rule_id": "silent-exception",
    "severity": "warning",
    "message": "Exception is caught and ignored ('pass'), which makes debugging difficult and can leave the database in an inconsistent state.",
    "line": 54,
    "suggestion": "Log the error or implement a proper recovery/rollback mechanism."
  }
]
```