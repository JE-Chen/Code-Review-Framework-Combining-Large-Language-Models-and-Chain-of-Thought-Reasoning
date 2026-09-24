- Code Smell Type: Global State / Thread Safety Issue
- Problem Location: `DATA_STORE = []`, `USER_COUNT = 0`, and the use of `global` keywords in `add_item()` and `reset_data()`.
- Detailed Explanation: The application uses global variables to store state. Flask is a multi-threaded framework; concurrent requests modifying `DATA_STORE` and `USER_COUNT` will lead to race conditions and data corruption. Furthermore, global state makes the application difficult to test in isolation and prevents horizontal scaling (state is lost if the app restarts or runs across multiple workers).
- Improvement Suggestions: Use a persistent database (e.g., PostgreSQL, Redis, or SQLite) to manage state. If a database is overkill for this specific use case, use a thread-safe data structure or a dedicated state management class.
- Priority Level: High

- Code Smell Type: Deeply Nested Conditionals (Arrow Anti-pattern)
- Problem Location: `complex_route()` function.
- Detailed Explanation: The function contains multiple levels of nested `if/else` blocks. This increases cognitive load, makes the logic harder to follow, and complicates the addition of new conditions. It violates the principle of keeping functions flat and readable.
- Improvement Suggestions: Use "Guard Clauses" to return early. For example, handle the `if not param` case first, then handle `isdigit()` and `param == "hello"` as separate top-level checks.
- Priority Level: Medium

- Code Smell Type: Overly Broad Exception Handling
- Problem Location: `add_item()` function: `except Exception as e:`.
- Detailed Explanation: Catching the base `Exception` class is dangerous because it hides unexpected errors (like `KeyboardInterrupt` or `MemoryError`) and makes debugging difficult. It also returns the raw exception string to the client, which can leak internal system details (security risk).
- Improvement Suggestions: Catch specific exceptions (e.g., `TypeError` or `KeyError` if the JSON payload is malformed). Implement a custom error handler or use Flask's `@app.errorhandler` to manage responses consistently.
- Priority Level: Medium

- Code Smell Type: Violation of Single Responsibility Principle (SRP)
- Problem Location: `get_items()` function.
- Detailed Explanation: The route handler is performing two distinct tasks: managing the HTTP request/response and implementing the business logic for filtering/transforming data based on `CONFIG`. As the transformation logic grows, the route handler will become bloated.
- Improvement Suggestions: Extract the data transformation logic into a separate service function or a helper class (e.g., `ItemService.format_items(data, config)`).
- Priority Level: Low