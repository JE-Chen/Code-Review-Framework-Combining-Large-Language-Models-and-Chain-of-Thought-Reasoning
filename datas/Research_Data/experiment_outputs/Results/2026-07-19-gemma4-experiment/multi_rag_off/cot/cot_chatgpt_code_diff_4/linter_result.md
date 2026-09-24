```json
[
  {
    "rule_id": "sql-injection",
    "severity": "error",
    "message": "Using f-strings to construct SQL queries allows for SQL injection attacks.",
    "line": 18,
    "suggestion": "Use parameterized queries: CURSOR.execute('INSERT INTO logs (msg, ts) VALUES (?, ?)', ('init-i', time.time()))"
  },
  {
    "rule_id": "sql-injection",
    "severity": "error",
    "message": "Using f-strings to construct SQL queries allows for SQL injection attacks.",
    "line": 25,
    "suggestion": "Use parameterized queries: CURSOR.execute('INSERT INTO logs (msg, ts) VALUES (?, ?)', (message, time.time()))"
  },
  {
    "rule_id": "sql-injection",
    "severity": "error",
    "message": "Concatenating variables into SQL strings allows for SQL injection attacks.",
    "line": 33,
    "suggestion": "Use parameterized queries for the LIMIT clause or validate that 'limit' is an integer."
  },
  {
    "rule_id": "silent-exception",
    "severity": "warning",
    "message": "Bare 'except Exception: pass' swallows all errors, making debugging and error recovery impossible.",
    "line": 53,
    "suggestion": "Catch specific exceptions or log the error before passing."
  },
  {
    "rule_id": "naming-convention",
    "severity": "info",
    "message": "Global variables 'CONN' and 'CURSOR' use uppercase naming, which is typically reserved for constants.",
    "line": 6,
    "suggestion": "Rename to 'conn' and 'cursor' or encapsulate them within a class/function."
  }
]
```