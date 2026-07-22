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
    "rule_id": "silent-exception",
    "severity": "warning",
    "message": "Bare 'except Exception: pass' suppresses all errors, making debugging difficult and hiding potential database failures.",
    "line": 53,
    "suggestion": "Catch specific exceptions or log the error instead of using 'pass'."
  },
  {
    "rule_id": "naming-convention",
    "severity": "info",
    "message": "Function name 'do_business_logic_but_sql_heavy' is overly verbose and non-standard.",
    "line": 41,
    "suggestion": "Rename to something more descriptive and concise, e.g., 'process_logs'."
  }
]
```