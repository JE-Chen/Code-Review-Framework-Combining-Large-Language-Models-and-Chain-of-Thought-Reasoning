```json
[
  {
    "rule_id": "shared-mutable-state",
    "severity": "error",
    "message": "Shared mutable state at the module level (CONN, CURSOR) can introduce hidden coupling and make the code difficult to test or run in parallel.",
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
    "message": "Concatenating variables directly into SQL strings allows for SQL injection.",
    "line": 31,
    "suggestion": "Use parameterized queries for the LIMIT clause or validate that 'limit' is strictly an integer."
  },
  {
    "rule_id": "environment-dependent-logic",
    "severity": "warning",
    "message": "Direct calls to system time (time.time()) make tests non-deterministic.",
    "line": 16,
    "suggestion": "Abstract the time provider or pass the timestamp as an argument to the function."
  },
  {
    "rule_id": "environment-dependent-logic",
    "severity": "warning",
    "message": "Direct calls to system time (time.time()) make tests non-deterministic.",
    "line": 23,
    "suggestion": "Abstract the time provider or pass the timestamp as an argument to the function."
  },
  {
    "rule_id": "environment-dependent-logic",
    "severity": "warning",
    "message": "Direct calls to random.choice/randint make the business logic non-deterministic and difficult to unit test.",
    "line": 26,
    "suggestion": "Inject a random number generator or pass the choice as a parameter."
  },
  {
    "rule_id": "empty-except",
    "severity": "warning",
    "message": "Bare 'except Exception: pass' swallows all errors, making debugging nearly impossible.",
    "line": 48,
    "suggestion": "Catch specific exceptions and log the error or handle it appropriately."
  },
  {
    "rule_id": "implicit-truthiness",
    "severity": "info",
    "message": "Relying on implicit truthiness for 'limit' (if limit:) may cause issues if 0 is a valid input.",
    "line": 30,
    "suggestion": "Use an explicit comparison: if limit is not None:"
  }
]
```