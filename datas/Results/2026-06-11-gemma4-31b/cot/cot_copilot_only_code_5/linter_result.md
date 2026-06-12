Following the provided global rules and the specific constraints of the "Strict Code Linter" prompt, here is the code review.

### Linter Messages

```json
[
  {
    "rule_id": "global-state-mutation",
    "severity": "error",
    "message": "Usage of a mutable global dictionary for state management leads to poor testability and potential concurrency issues.",
    "line": 1,
    "suggestion": "Encapsulate state within a class or pass state objects as arguments to functions."
  },
  {
    "rule_id": "magic-number",
    "severity": "warning",
    "message": "The value '77' is a magic number without a descriptive constant name.",
    "line": 5,
    "suggestion": "Define a constant such as DEFAULT_THRESHOLD = 77."
  },
  {
    "rule_id": "magic-number",
    "severity": "warning",
    "message": "The range limit '21' is a magic number.",
    "line": 10,
    "suggestion": "Define a constant for the data limit (e.g., DATA_SIZE = 20)."
  },
  {
    "rule_id": "cognitive-complexity",
    "severity": "info",
    "message": "The process_items function contains deeply nested conditional logic (if/else inside if/else).",
    "line": 24,
    "suggestion": "Extract the item processing logic into a separate helper function to improve readability."
  },
  {
    "rule_id": "missing-docstrings",
    "severity": "info",
    "message": "Functions lack docstrings explaining their purpose, arguments, and return values.",
    "line": 9,
    "suggestion": "Add PEP 257 compliant docstrings to all function definitions."
  }
]
```

---

### Review Summary (Global Rules Assessment)

1.  **Readability & Consistency**: The formatting is consistent, but the lack of documentation (docstrings) makes the intent of the logic less clear to external developers.
2.  **Naming Conventions**: Variable names are generally clear, though `GLOBAL_STATE` follows constant naming (uppercase) while being mutated throughout the program.
3.  **Software Engineering Standards**: The code suffers from high coupling due to the global state. It is difficult to unit test `process_items` or `increment_counter` in isolation without resetting a global object.
4.  **Logic & Correctness**: The logic is correct for its current simple implementation; however, there is no input validation or error handling for the state dictionary keys.
5.  **Performance & Security**: Performance is optimal for the current scale. No significant security risks identified, though global state is a risk in multi-threaded environments.
6.  **Documentation & Testing**: There are no unit tests provided, and no documentation exists to explain the "business logic" behind the threshold or the flag transformations.