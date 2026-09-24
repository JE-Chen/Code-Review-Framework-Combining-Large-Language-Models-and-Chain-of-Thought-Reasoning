```json
[
  {
    "rule_id": "shared-mutable-state",
    "severity": "warning",
    "message": "Shared mutable state at the module level (CONN, CURSOR) can introduce hidden coupling and make testing difficult.",
    "line": 6,
    "suggestion": "Encapsulate the database connection and cursor within a class or pass them as arguments to functions."
  },
  {
    "rule_id": "sql-injection",
    "severity": "error",
    "message": "Using f-strings to construct SQL queries allows for SQL injection attacks.",
    "line": 16,
    "suggestion": "Use parameterized queries: CURSOR.execute('INSERT INTO logs (msg, ts) VALUES (?, ?)', ('init-i', time.time()))"
  },
  {
    "rule_id": "sql-injection",
    "severity": "error",
    "message": "Using f-strings to construct SQL queries allows for SQL injection attacks.",
    "line": 23,
    "suggestion": "Use parameterized queries: CURSOR.execute('INSERT INTO logs (msg, ts) VALUES (?, ?)', (message, time.time()))"
  },
  {
    "rule_id": "sql-injection",
    "severity": "error",
    "message": "Concatenating variables into SQL strings allows for SQL injection attacks.",
    "line": 32,
    "suggestion": "Use parameterized queries for the LIMIT clause or validate that 'limit' is a strict integer."
  },
  {
    "rule_id": "broad-exception",
    "severity": "warning",
    "message": "Catching a broad exception (Exception) can hide real bugs and make debugging difficult.",
    "line": 53,
    "suggestion": "Catch specific sqlite3 exceptions (e.g., sqlite3.Error) and handle them intentionally."
  },
  {
    "rule_id": "empty-except-block",
    "severity": "warning",
    "message": "The except block contains only 'pass', which silently swallows errors.",
    "line": 54,
    "suggestion": "Log the error or implement a recovery strategy instead of ignoring it."
  },
  {
    "rule_id": "environment-dependency",
    "severity": "info",
    "message": "Direct calls to time.time() and random.choice() make the logic non-deterministic and harder to test.",
    "line": 16,
    "suggestion": "Abstract time and randomness into a provider or pass them as arguments to improve testability."
  }
]
```