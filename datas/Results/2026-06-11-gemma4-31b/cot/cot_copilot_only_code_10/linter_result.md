Based on the global rules provided, here is the code review.

### 1. Readability & Consistency
- **Formatting:** The code is generally well-formatted and follows standard Python indentation.
- **Consistency:** The use of global variables (`SESSION`, `GLOBAL_CACHE`) contrasts with the object-oriented approach of `APIClient`, creating a hybrid style that is inconsistent.

### 2. Naming Conventions
- **Descriptive Names:** Variables like `u`, `p`, and `t` in `process_all()` are too concise. They should be `user`, `post`, and `todo` to improve semantic clarity.

### 3. Software Engineering Standards
- **Modularization/DRY:** The functions `get_users`, `get_posts`, and `get_todos` are nearly identical. This is a violation of the "Avoid duplicate code" rule. These should be abstracted into a single generic function.
- **Global State:** `GLOBAL_CACHE` is used as a global mutable variable, which makes the code harder to test and can lead to side effects in multi-threaded environments.
- **Dependency Injection:** While `APIClient` is passed to functions, the `SESSION` object is hardcoded globally inside `APIClient.fetch`, hindering mock-testing.

### 4. Logic & Correctness
- **Error Handling:** `APIClient.fetch` returns a dictionary on failure (e.g., `{"error": "..."}`). However, `process_all` assumes the return value is always a list (`for u in users`). If an API error occurs, the code will crash with a `TypeError: 'dict' object is not iterable`.
- **String Concatenation:** Using `+` for string concatenation in error messages and results is less idiomatic and performant than f-strings in modern Python.

### 5. Performance & Security
- **Input Validation:** `BASE_URL` and `endpoint` are concatenated using `+`. While not a critical vulnerability here, using `urllib.parse.urljoin` is the industry standard to prevent issues with trailing/leading slashes.
- **Resource Management:** The `SESSION` is global and never explicitly closed.

### 6. Documentation & Testing
- **Documentation:** There are no docstrings for the class or functions.
- **Testing:** No unit tests or integration tests are provided.

---

### Linter Messages

```json
[
  {
    "rule_id": "no-generic-exception",
    "severity": "warning",
    "message": "Catching a broad Exception can hide unexpected bugs.",
    "line": 21,
    "suggestion": "Catch specific exceptions like requests.exceptions.RequestException."
  },
  {
    "rule_id": "duplicate-logic",
    "severity": "warning",
    "message": "Functions get_users, get_posts, and get_todos share identical logic patterns.",
    "line": 24,
    "suggestion": "Create a generic function: fetch_and_cache(client, endpoint, cache_key)."
  },
  {
    "rule_id": "potential-type-error",
    "severity": "error",
    "message": "The code iterates over API responses without verifying if they are lists or error dictionaries.",
    "line": 41,
    "suggestion": "Check if 'error' is in the response before starting the loop."
  },
  {
    "rule_id": "poor-variable-naming",
    "severity": "info",
    "message": "Variable names 'u', 'p', 't' are not descriptive.",
    "line": 41,
    "suggestion": "Rename to 'user', 'post', and 'todo'."
  },
  {
    "rule_id": "global-mutable-state",
    "severity": "warning",
    "message": "Use of GLOBAL_CACHE makes the code less maintainable and harder to test.",
    "line": 8,
    "suggestion": "Move the cache into the APIClient class or a dedicated Cache manager."
  },
  {
    "rule_id": "deeply-nested-conditionals",
    "severity": "info",
    "message": "Excessive nesting of if/else statements reduces readability.",
    "line": 62,
    "suggestion": "Use elif statements to flatten the logic."
  },
  {
    "rule_id": "missing-documentation",
    "severity": "info",
    "message": "Class APIClient and its methods lack docstrings.",
    "line": 11,
    "suggestion": "Add PEP 257 compliant docstrings."
  }
]
```