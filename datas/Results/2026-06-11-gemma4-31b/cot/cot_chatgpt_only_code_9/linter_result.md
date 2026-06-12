Based on the provided global rules and the specific requirements of the "strict code linter" prompt, here is the code review.

### Linter Messages

```json
[
  {
    "rule_id": "global-mutable-state",
    "severity": "warning",
    "message": "Use of global variable 'GLOBAL_CACHE' can lead to side effects and makes the code harder to test and thread-unsafe.",
    "line": 7,
    "suggestion": "Encapsulate the cache within a class or pass a cache object as a dependency."
  },
  {
    "rule_id": "url-concatenation",
    "severity": "warning",
    "message": "Using simple string concatenation for URLs can lead to malformed URLs (e.g., double slashes).",
    "line": 15,
    "suggestion": "Use 'urllib.parse.urljoin' or a library like 'httpx' for safe URL construction."
  },
  {
    "rule_id": "broad-exception-catch",
    "severity": "error",
    "message": "Catching all exceptions ('Exception') masks potential bugs and makes debugging difficult.",
    "line": 21,
    "suggestion": "Catch specific exceptions such as 'requests.exceptions.RequestException'."
  },
  {
    "rule_id": "code-duplication",
    "severity": "info",
    "message": "Functions 'get_users', 'get_posts', and 'get_todos' follow an identical pattern.",
    "line": 24,
    "suggestion": "Refactor into a single generic function: 'get_data(client, resource)'."
  },
  {
    "rule_id": "naming-convention",
    "severity": "info",
    "message": "Variable name 'u', 'p', and 't' are not descriptive.",
    "line": 42,
    "suggestion": "Use meaningful names like 'user', 'post', and 'todo'."
  },
  {
    "rule_id": "potential-key-error",
    "severity": "error",
    "message": "Accessing p['title'] directly without using .get() or checking existence after using .get() in the previous line.",
    "line": 46,
    "suggestion": "Use 'p.get(\"title\")' to remain consistent and avoid KeyError."
  },
  {
    "rule_id": "deeply-nested-logic",
    "severity": "warning",
    "message": "The nested if-else structure in main() reduces readability.",
    "line": 61,
    "suggestion": "Use an 'if-elif-else' chain to flatten the logic."
  },
  {
    "rule_id": "missing-type-hints",
    "severity": "info",
    "message": "Functions lack type annotations for arguments and return values.",
    "line": 12,
    "suggestion": "Add Python type hints (e.g., 'def fetch(self, endpoint: str) -> dict:')."
  }
]
```

---

### Summary Analysis (per Global Rules)

1.  **Readability & Consistency**: The formatting is consistent, but the logic in `main()` is unnecessarily nested, impacting readability.
2.  **Naming Conventions**: The use of single-letter variables (`u`, `p`, `t`) violates the requirement for descriptive and meaningful names.
3.  **Software Engineering Standards**: The code suffers from duplication in the `get_*` functions. It relies on global state (`GLOBAL_CACHE`), which hinders modularity and testability.
4.  **Logic & Correctness**: There is a potential `KeyError` on line 46 because it accesses `p["title"]` directly, while other parts of the code safely use `.get()`.
5.  **Performance & Security**: The use of a global `requests.Session()` is a good performance practice. However, the broad exception handling could hide critical system failures.
6.  **Documentation & Testing**: There are no docstrings or unit tests provided for the logic.