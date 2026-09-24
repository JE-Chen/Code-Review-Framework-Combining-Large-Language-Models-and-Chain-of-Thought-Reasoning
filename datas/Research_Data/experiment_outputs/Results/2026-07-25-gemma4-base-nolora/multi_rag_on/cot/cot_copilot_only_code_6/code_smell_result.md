- Code Smell Type: Shared Mutable State
- Problem Location: `DATA_STORE = []`, `USER_COUNT = 0`, and the use of `global` keywords in `add_item()` and `reset_data()`.
- Detailed Explanation: The application uses global variables to maintain state. In a production Flask environment (which typically uses multi-threading or multi-process workers like Gunicorn), these globals are not thread-safe and will not be shared across different worker processes. This leads to inconsistent data and race conditions.
- Improvement Suggestions: Use a proper database (e.g., PostgreSQL, SQLite) or a distributed cache (e.g., Redis) to persist state. If a simple in-memory store is required for testing, encapsulate the state within a Repository class or a Singleton pattern with appropriate locking mechanisms.
- Priority Level: High

- Code Smell Type: Deeply Nested Conditional Logic (Arrow Anti-pattern)
- Problem Location: `complex_route()` function.
- Detailed Explanation: The function contains four levels of nested `if/else` statements. This increases cognitive load, makes the code harder to read, and complicates the addition of new conditions. It violates the principle of keeping control flow flat.
- Improvement Suggestions: Use **Guard Clauses** to return early. For example, handle the `if not param` case first, then handle `isdigit()` and `param == "hello"` as separate top-level checks.
- Priority Level: Medium

- Code Smell Type: Violation of Single Responsibility Principle (SRP)
- Problem Location: `get_items()` function.
- Detailed Explanation: This function is responsible for three different things: iterating through the data store, applying business logic based on the `CONFIG` mode (filtering/truncating), and formatting the HTTP response. Mixing business logic with the routing layer makes the logic difficult to unit test without mocking the entire Flask request context.
- Improvement Suggestions: Extract the logic for processing items into a separate service function (e.g., `process_items(data, config)`). The route handler should only be responsible for calling the service and returning the JSON response.
- Priority Level: Medium

- Code Smell Type: Generic Exception Handling
- Problem Location: `add_item()` function: `except Exception as e:`
- Detailed Explanation: Catching the base `Exception` class is too broad. It can hide unexpected bugs (like `TypeError` or `KeyError`) that should ideally crash during development or be logged specifically, rather than being returned as a generic error message to the client.
- Improvement Suggestions: Catch specific exceptions (e.g., `TypeError` if `request.json` is None) and implement a global error handler using `@app.errorhandler` to manage API responses consistently.
- Priority Level: Low