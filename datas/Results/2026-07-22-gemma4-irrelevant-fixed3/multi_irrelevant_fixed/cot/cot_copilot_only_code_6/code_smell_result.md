- Code Smell Type: Global State Dependency
- Problem Location: `DATA_STORE = []`, `USER_COUNT = 0`, and the use of `global` keywords in `add_item()` and `reset_data()`.
- Detailed Explanation: The application relies on global variables to maintain state. This makes the code difficult to test in isolation, prevents the app from being thread-safe (Flask's default server handles multiple requests), and will cause data loss or inconsistency if the app is deployed across multiple worker processes (e.g., using Gunicorn or uWSGI).
- Improvement Suggestions: Replace global variables with a persistent database (e.g., PostgreSQL, SQLite) or a caching layer (e.g., Redis). If a simple in-memory store is required for testing, encapsulate the state within a Class or a Repository pattern.
- Priority Level: High

- Code Smell Type: Deeply Nested Conditionals (Arrow Anti-pattern)
- Problem Location: `complex_route()` function.
- Detailed Explanation: The function contains multiple levels of nested `if/else` blocks. This increases cognitive load, makes the logic harder to follow, and complicates the addition of new conditions, leading to poor maintainability.
- Improvement Suggestions: Use "Guard Clauses" to return early. For example, handle the `if not param` case first, then handle `isdigit()` and `param == "hello"` as separate top-level checks to flatten the structure.
- Priority Level: Medium

- Code Smell Type: Generic Exception Handling
- Problem Location: `add_item()` function: `except Exception as e:`.
- Detailed Explanation: Catching the base `Exception` class is too broad. It masks unexpected bugs (like `TypeError` or `AttributeError`) and returns them as generic API errors, which makes debugging difficult and can potentially leak internal system details to the client.
- Improvement Suggestions: Catch specific exceptions (e.g., `TypeError` if `request.json` is None) and implement a global error handler using `@app.errorhandler` to manage unexpected failures consistently.
- Priority Level: Medium

- Code Smell Type: Violation of Single Responsibility Principle (SRP)
- Problem Location: `get_items()` function.
- Detailed Explanation: The route handler is performing two distinct tasks: managing the HTTP request/response and implementing the business logic for filtering/transforming data based on `CONFIG`. This makes the business logic non-reusable and harder to unit test without mocking the Flask request context.
- Improvement Suggestions: Extract the logic for processing items into a separate service function (e.g., `process_items(data, config)`) and call that function from the route handler.
- Priority Level: Low