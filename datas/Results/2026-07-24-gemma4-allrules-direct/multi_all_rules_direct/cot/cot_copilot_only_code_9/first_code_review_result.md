### Code Review

**Logic & Correctness**
* **Broad Exception Handling:** `get_users`, `get_posts`, and `get_comments` use `except Exception:`. This can hide critical errors (like `KeyboardInterrupt` or `ConnectionError`). Catch specific `requests` exceptions instead.
* **Implicit Truthiness:** In `main()`, `if len(GLOBAL_RESULTS) > 0:` is used. While correct, explicit checks or leveraging Python's truthiness for containers is preferred, but the nested logic here is the primary concern.

**Software Engineering Standards**
* **Shared Mutable State:** The use of `GLOBAL_RESULTS` as a module-level list introduces hidden coupling. `process_data` should return a list, and `main` should handle the result.
* **Code Duplication:** The three `get_*` functions are nearly identical. These should be refactored into a single generic `fetch_data(endpoint)` function to improve maintainability.
* **Deeply Nested Logic:** The result-count logic in `main()` is deeply nested. Use guard clauses or a flatter `if/elif/else` structure to reduce cognitive load.

**Naming Conventions**
* **Non-Descriptive Variables:** In `process_data`, variables `u`, `p`, and `c` are too cryptic. Use `user`, `post`, and `comment`.

**Performance & Security**
* **Input Validation:** The code assumes `response.json()` will always return a list. If the API returns an error object or unexpected format, the subsequent loops will crash.

**Suggested Improvements**
* **Refactor API calls:** Create one function `fetch_resource(resource_name)` to replace the three redundant functions.
* **Remove Global State:** Pass data explicitly between `process_data()` and `main()`.
* **Flatten Conditionals:** Replace the nested `if` statements in `main()` with a clean `if/elif/else` chain.
* **Specific Exceptions:** Change `except Exception` to `except requests.RequestException`.