- Code Smell Type: Duplicate Code (Boilerplate)
- Problem Location: `get_users()`, `get_posts()`, and `get_comments()` functions.
- Detailed Explanation: These three functions are nearly identical, differing only in the endpoint string. This violates the DRY (Don't Repeat Yourself) principle. If the error handling logic or the way requests are made needs to change (e.g., adding a timeout or changing the logging mechanism), it must be updated in three separate places, increasing the risk of inconsistency and bugs.
- Improvement Suggestions: Create a single generic helper function, e.g., `fetch_data(endpoint)`, that accepts the endpoint as an argument and handles the request and exception logic.
- Priority Level: High

- Code Smell Type: Use of Global State
- Problem Location: `GLOBAL_RESULTS = []` and its usage in `process_data()` and `main()`.
- Detailed Explanation: Relying on a global list to store results makes the code harder to test, debug, and reuse. It creates hidden dependencies between functions, meaning `process_data()` cannot be called multiple times without manually clearing the global list, and it prevents the code from being thread-safe or modular.
- Improvement Suggestions: Refactor `process_data()` to return a list of results and pass that list as an argument to `main()` or any other function that needs it.
- Priority Level: High

- Code Smell Type: Overly Broad Exception Handling
- Problem Location: `except Exception as e:` in all `get_*` functions.
- Detailed Explanation: Catching the base `Exception` class is too broad. It catches not only network errors (like `requests.exceptions.RequestException`) but also system-level errors or programming errors (like `KeyboardInterrupt` or `NameError`), which can mask bugs and make troubleshooting difficult.
- Improvement Suggestions: Catch specific exceptions provided by the `requests` library (e.g., `requests.exceptions.RequestException`) and implement a more robust logging strategy than `print`.
- Priority Level: Medium

- Code Smell Type: Deeply Nested Conditionals (Arrow Anti-pattern)
- Problem Location: The `if/else` block inside `main()` used to categorize the number of results.
- Detailed Explanation: The nested `if` statements for checking the length of `GLOBAL_RESULTS` reduce readability and increase cognitive load. As more categories are added, the nesting will deepen, making the logic harder to follow.
- Improvement Suggestions: Use a "guard clause" to handle the empty case first, and then use `elif` statements to flatten the logic.
- Priority Level: Low