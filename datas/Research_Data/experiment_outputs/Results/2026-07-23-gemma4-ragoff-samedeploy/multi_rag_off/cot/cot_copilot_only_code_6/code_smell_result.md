- Code Smell Type: Global State Dependency
- Problem Location: `DATA_STORE = []`, `USER_COUNT = 0`, and the use of `global` keywords in `add_item()` and `reset_data()`.
- Detailed Explanation: The application relies on global variables to manage state. This makes the code difficult to test in isolation, prevents thread-safe operations (Flask is multi-threaded by default), and will cause data loss or inconsistency if the app is deployed across multiple worker processes (e.g., using Gunicorn).
- Improvement Suggestions: Replace global variables with a proper database (e.g., PostgreSQL, SQLite) or a caching layer (e.g., Redis). If a simple in-memory store is required for testing, encapsulate the state within a Class or a Repository pattern.
- Priority Level: High

- Code Smell Type: Deeply Nested Conditionals (Arrow Anti-pattern)
- Problem Location: `complex_route()` function.
- Detailed Explanation: The function contains multiple levels of nested `if/else` blocks. This increases cognitive load, makes the logic harder to follow, and complicates the addition of new conditions, leading to poor maintainability.
- Improvement Suggestions: Use "Guard Clauses" to return early. For example, handle the `if not param` case first, then handle `isdigit()` and `param == "hello"` as separate top-level checks to flatten the structure.
- Priority Level: Medium

- Code Smell Type: Generic Exception Handling
- Problem Location: `add_item()` function: `except Exception as e:`.
- Detailed Explanation: Catching the base `Exception` class is too broad. It can hide unexpected bugs (like `TypeError` or `KeyError`) and returns the raw exception string to the client, which can leak internal implementation details and pose a security risk.
- Improvement Suggestions: Catch specific exceptions (e.g., `TypeError` if `request.json` is None) and implement a structured error response. Use a global error handler in Flask (`@app.errorhandler`) for unexpected crashes.
- Priority Level: Medium

- Code Smell Type: Violation of Single Responsibility Principle (SRP)
- Problem Location: `get_items()` function.
- Detailed Explanation: The route handler is responsible for both the HTTP request/response logic and the business logic for filtering and transforming data based on `CONFIG`. This makes the transformation logic non-reusable and harder to unit test.
- Improvement Suggestions: Extract the item transformation logic into a separate service function or a helper method (e.g., `transform_item(item, config)`).
- Priority Level: Low