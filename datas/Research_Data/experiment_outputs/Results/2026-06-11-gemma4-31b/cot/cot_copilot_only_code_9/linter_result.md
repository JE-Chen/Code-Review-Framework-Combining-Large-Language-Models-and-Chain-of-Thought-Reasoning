### Code Review Report

Based on the global rules provided, here is the detailed code review of the submitted script.

#### 1. Readability & Consistency
- **Formatting:** The code follows basic PEP 8 indentation and spacing.
- **Consistency:** The error handling pattern is consistent across the three fetch functions.

#### 2. Naming Conventions
- **Variable Names:** While names like `u`, `p`, `c`, and `r` are used in loops, they are too concise and lack descriptive meaning, hindering readability.
- **Constants:** `BASE_URL` and `HEADERS` are correctly named as constants.

#### 3. Software Engineering Standards
- **Modularity:** There is significant code duplication. `get_users`, `get_posts`, and `get_comments` perform identical logic with different endpoints. This should be abstracted into a single generic fetch function.
- **State Management:** The use of a global variable `GLOBAL_RESULTS` is a bad practice. It makes the code harder to test, prevents thread safety, and creates hidden dependencies between `process_data` and `main`.

#### 4. Logic & Correctness
- **Error Handling:** The code uses a "catch-all" `except Exception`, which can hide critical bugs (like `KeyboardInterrupt` or `MemoryError`).
- **API Validation:** `response.json()` is called without checking `response.status_code` or calling `response.raise_for_status()`. If the API returns a 404 or 500 error, the code may crash or process invalid data.
- **Data Access:** There is an inconsistency in data access. The code uses `.get()` for checks but direct key access (e.g., `p["title"]`) for appending. If the key is missing, a `KeyError` will be raised.

#### 5. Performance & Security
- **Performance:** The requests are synchronous and sequential. Fetching users, posts, and comments one after another increases total execution time.
- **Security:** While the URL is hardcoded here, the lack of timeout in `requests.get()` is a risk; the program could hang indefinitely if the server does not respond.

#### 6. Documentation & Testing
- **Documentation:** The code lacks docstrings for functions and a module-level explanation.
- **Testing:** No unit tests or integration tests are provided.

---

### Linter Messages

```json
[
  {
    "rule_id": "duplicated-code",
    "severity": "warning",
    "message": "Functions get_users, get_posts, and get_comments share identical logic. Refactor into a single request helper function.",
    "line": 8,
    "suggestion": "Create a function `fetch_resource(endpoint)` to handle the requests."
  },
  {
    "rule_id": "global-state",
    "severity": "error",
    "message": "Avoid using global variables for data storage (GLOBAL_RESULTS). This impairs maintainability and testability.",
    "line": 5,
    "suggestion": "Have process_data() return a list and pass it as an argument to main()."
  },
  {
    "rule_id": "broad-exception",
    "severity": "warning",
    "message": "Using 'except Exception' catches all exceptions, including system exits and interrupts.",
    "line": 11,
    "suggestion": "Catch specific exceptions like 'requests.exceptions.RequestException'."
  },
  {
    "rule_id": "unhandled-http-error",
    "severity": "error",
    "message": "HTTP response status is not verified before calling .json().",
    "line": 10,
    "suggestion": "Add 'response.raise_for_status()' before returning the JSON data."
  },
  {
    "rule_id": "unclear-variable-name",
    "severity": "info",
    "message": "Variable names 'u', 'p', 'c', and 'r' are not descriptive.",
    "line": 35,
    "suggestion": "Use 'user', 'post', 'comment', and 'result' instead."
  },
  {
    "rule_id": "potential-key-error",
    "severity": "warning",
    "message": "Direct dictionary access 'p[\"title\"]' and 'c[\"email\"]' may raise KeyError if the key is missing.",
    "line": 40,
    "suggestion": "Use the .get() method consistently: p.get('title', 'Unknown')."
  },
  {
    "rule_id": "missing-timeout",
    "severity": "warning",
    "message": "Requests made without a timeout can hang the application indefinitely.",
    "line": 10,
    "suggestion": "Add a timeout parameter: requests.get(..., timeout=10)."
  },
  {
    "rule_id": "deeply-nested-logic",
    "severity": "info",
    "message": "Deeply nested if-else blocks in main() reduce readability.",
    "line": 50,
    "suggestion": "Use elif statements to flatten the conditional logic."
  }
]
```