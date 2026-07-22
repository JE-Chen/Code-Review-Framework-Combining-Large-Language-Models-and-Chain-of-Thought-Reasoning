- Code Smell Type: Duplicate Code (Boilerplate)
- Problem Location: `get_users()`, `get_posts()`, and `get_comments()` functions.
- Detailed Explanation: These three functions are nearly identical, differing only by the endpoint string. This violates the DRY (Don't Repeat Yourself) principle. If the error handling logic or the way requests are made needs to change (e.g., adding a timeout or changing the logging mechanism), it must be updated in three separate places, increasing the risk of inconsistency and bugs.
- Improvement Suggestions: Create a generic helper function, e.g., `fetch_data(endpoint)`, that accepts the endpoint as an argument and handles the request and exception logic.
- Priority Level: High

- Code Smell Type: Global State / Tight Coupling
- Problem Location: `GLOBAL_RESULTS = []` and its usage in `process_data()` and `main()`.
- Detailed Explanation: Using a global list to store results makes the code harder to test and reason about. `process_data()` has a side effect of modifying a global variable rather than returning a value. This prevents the function from being reused in different contexts and can lead to unpredictable behavior if the script were to be expanded to run multiple processes or tests.
- Improvement Suggestions: Refactor `process_data()` to return a list of results, and pass that list as an argument to `main()` or the printing logic.
- Priority Level: High

- Code Smell Type: Overly Broad Exception Handling
- Problem Location: `except Exception as e:` in all `get_*` functions.
- Detailed Explanation: Catching the base `Exception` class is too broad. It catches not only network errors (like `requests.exceptions.RequestException`) but also system-level errors or programming errors (like `KeyboardInterrupt` or `NameError`), which can mask bugs and make debugging difficult.
- Improvement Suggestions: Catch specific exceptions provided by the `requests` library (e.g., `requests.exceptions.RequestException`).
- Priority Level: Medium

- Code Smell Type: Deeply Nested Conditionals (Arrow Anti-pattern)
- Problem Location: The `if/else` block inside `main()` used to categorize the number of results.
- Detailed Explanation: The nested `if` statements for checking the length of `GLOBAL_RESULTS` create unnecessary indentation and reduce readability. This structure becomes increasingly difficult to maintain as more categories are added.
- Improvement Suggestions: Use a "guard clause" approach or a more linear structure. Since these are mutually exclusive ranges, using `elif` would flatten the logic and make it significantly clearer.
- Priority Level: Low