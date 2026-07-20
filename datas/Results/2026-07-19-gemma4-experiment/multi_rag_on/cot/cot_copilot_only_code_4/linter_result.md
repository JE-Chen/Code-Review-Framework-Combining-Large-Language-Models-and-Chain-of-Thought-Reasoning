```json
[
  {
    "rule_id": "magic-number",
    "severity": "warning",
    "message": "The function returns a magic number (9999) to indicate a ZeroDivisionError, which can be confused with a valid result.",
    "line": 5,
    "suggestion": "Raise a custom exception or return None/Optional to explicitly handle the error state."
  },
  {
    "rule_id": "magic-number",
    "severity": "warning",
    "message": "The function returns a magic number (-1) to indicate a general exception.",
    "line": 8,
    "suggestion": "Raise the exception or return a consistent error indicator."
  },
  {
    "rule_id": "magic-number",
    "severity": "warning",
    "message": "The function returns a magic number (-999) to indicate a general exception.",
    "line": 15,
    "suggestion": "Raise the exception or return a consistent error indicator."
  },
  {
    "rule_id": "resource-leak",
    "severity": "error",
    "message": "File is opened manually and closed at the end of the try block. If an exception occurs during f.read(), f.close() will never be called.",
    "line": 18,
    "suggestion": "Use a 'with open(filename, \"r\") as f:' statement to ensure the file is closed automatically."
  },
  {
    "rule_id": "broad-exception",
    "severity": "warning",
    "message": "Catching a generic 'Exception' can hide unexpected bugs and makes debugging difficult.",
    "line": 24,
    "suggestion": "Catch specific exceptions that are expected to occur."
  },
  {
    "rule_id": "broad-exception",
    "severity": "warning",
    "message": "Nested try-except block with a broad 'Exception' catch is redundant and obscures the logic.",
    "line": 31,
    "suggestion": "Remove the inner try-except or catch a specific exception."
  },
  {
    "rule_id": "broad-exception",
    "severity": "warning",
    "message": "Catching a generic 'Exception' at the top level of process_data may mask critical failures.",
    "line": 37,
    "suggestion": "Catch specific exceptions or allow them to propagate to the caller."
  }
]
```