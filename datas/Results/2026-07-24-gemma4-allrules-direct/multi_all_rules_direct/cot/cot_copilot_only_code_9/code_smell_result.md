- Code Smell Type: Shared Mutable State
- Problem Location: `GLOBAL_RESULTS = []` and its usage in `process_data()`
- Detailed Explanation: The use of a global list to store results introduces hidden coupling between `process_data` and `main`. This makes the code difficult to test in isolation, as the state persists across function calls, and can lead to unpredictable behavior if the program were to become multi-threaded or if `process_data` were called multiple times.
- Improvement Suggestions: Refactor `process_data` to return a list of results and pass that list as an argument to the function that prints them.
- Priority Level: High

- Code Smell Type: Duplicate Code / Lack of Abstraction
- Problem Location: `get_users()`, `get_posts()`, and `get_comments()`
- Detailed Explanation: These three functions are nearly identical, differing only by the endpoint string. This violates the DRY (Don't Repeat Yourself) principle, increasing maintenance effort; if the error handling or request logic needs to change, it must be updated in three places.
- Improvement Suggestions: Create a single generic helper function, e.g., `fetch_data(endpoint)`, that takes the endpoint as a parameter and handles the request and exception logic.
- Priority Level: Medium

- Code Smell Type: Broad Exception Handling
- Problem Location: `except Exception as e:` in all `get_*` functions.
- Detailed Explanation: Catching the base `Exception` class can hide unexpected bugs (like `KeyboardInterrupt` or `MemoryError`) and makes debugging difficult because it doesn't distinguish between a network timeout, a 404 error, or a JSON parsing error.
- Improvement Suggestions: Catch specific exceptions provided by the `requests` library, such as `requests.exceptions.RequestException`.
- Priority Level: Medium

- Code Smell Type: Deeply Nested Conditional Logic
- Problem Location: The `if/else` block inside `main()` checking `len(GLOBAL_RESULTS)`.
- Detailed Explanation: The nested structure increases cognitive load and makes the logic harder to follow. This is a classic case where guard clauses or a flatter structure would improve readability.
- Improvement Suggestions: Use early returns or a flat `if/elif/else` structure to handle the result count categories.
- Priority Level: Low

- Code Smell Type: Unclear Naming
- Problem Location: `for u in users:`, `for p in posts:`, `for c in comments:`
- Detailed Explanation: Single-letter variable names (`u`, `p`, `c`) are ambiguous. While the context is small here, in larger functions, this reduces readability and makes the code less self-explanatory.
- Improvement Suggestions: Use descriptive names such as `user`, `post`, and `comment`.
- Priority Level: Low