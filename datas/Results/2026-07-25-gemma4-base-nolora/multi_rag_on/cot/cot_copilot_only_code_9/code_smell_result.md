- Code Smell Type: Duplicate Code (Dry Principle Violation)
- Problem Location: `get_users()`, `get_posts()`, and `get_comments()` functions.
- Detailed Explanation: These three functions are nearly identical, differing only by the endpoint string. This duplication increases maintenance overhead; if the error handling logic or the way requests are made needs to change (e.g., adding a timeout or changing the logging mechanism), it must be updated in three separate places.
- Improvement Suggestions: Create a single generic helper function, such as `fetch_data(endpoint)`, that accepts the path as an argument and handles the request and exception logic.
- Priority Level: High

- Code Smell Type: Use of Global State
- Problem Location: `GLOBAL_RESULTS = []` and its usage in `process_data()` and `main()`.
- Detailed Explanation: Relying on a global list to store results makes the code harder to test, debug, and scale. It creates tight coupling between `process_data` and `main`, and prevents the code from being thread-safe or reusable in a larger application where multiple data processing tasks might run concurrently.
- Improvement Suggestions: Refactor `process_data()` to return a list of results instead of appending to a global variable. Pass this returned list as an argument to the printing logic in `main()`.
- Priority Level: High

- Code Smell Type: Overly Broad Exception Handling
- Problem Location: `except Exception as e:` in all `get_*` functions.
- Detailed Explanation: Catching the base `Exception` class is a bad practice because it catches everything, including keyboard interrupts (Ctrl+C) or system exits, and hides the specific nature of the failure (e.g., DNS failure vs. 404 Not Found vs. JSON decoding error).
- Improvement Suggestions: Catch specific exceptions provided by the `requests` library, such as `requests.exceptions.RequestException`.
- Priority Level: Medium

- Code Smell Type: Deeply Nested Conditionals (Arrow Anti-pattern)
- Problem Location: The `if/else` block inside `main()` used to categorize the number of results.
- Detailed Explanation: The nested `if` statements for checking the length of `GLOBAL_RESULTS` reduce readability. As more categories are added, the indentation will continue to shift right, making the logic harder to follow.
- Improvement Suggestions: Use a "guard clause" to handle the empty list case first, then use `elif` statements to flatten the logic.
- Priority Level: Low