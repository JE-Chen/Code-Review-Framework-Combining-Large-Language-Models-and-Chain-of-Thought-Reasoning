- Code Smell Type: Global State / Tight Coupling
- Problem Location: `DATA_STORE = []`, `USER_COUNT = 0`, and the use of `global` keywords in `add_item()` and `reset_data()`.
- Detailed Explanation: The application relies on global variables to manage state. This makes the code difficult to test in isolation, prevents the app from being thread-safe (Flask's default server handles multiple requests), and creates tight coupling between the routes and the data storage. In a production environment, this would lead to data corruption or loss upon server restart.
- Improvement Suggestions: Implement a Repository pattern or use a database (e.g., SQLite, PostgreSQL). If a simple in-memory store is required for testing, encapsulate the state within a class or a separate data management module.
- Priority Level: High

- Code Smell Type: Deeply Nested Conditionals (Arrow Anti-pattern)
- Problem Location: `complex_route()` function.
- Detailed Explanation: The function contains multiple levels of nested `if/else` statements. This significantly reduces readability and increases cognitive load, making it harder to maintain or modify the logic without introducing bugs.
- Improvement Suggestions: Use "Guard Clauses" to return early. For example, handle the `if not param` case first, then handle `if not param.isdigit()`, flattening the structure.
- Priority Level: Medium

- Code Smell Type: Overly Broad Exception Handling
- Problem Location: `add_item()` function: `except Exception as e:`.
- Detailed Explanation: Catching the base `Exception` class is dangerous because it hides unexpected errors (like `KeyboardInterrupt` or `MemoryError`) and makes debugging difficult. Furthermore, returning `str(e)` directly to the client can leak internal system details (security risk).
- Improvement Suggestions: Catch specific exceptions (e.g., `TypeError`, `KeyError`) and implement a structured error response that does not expose raw exception strings to the end user.
- Priority Level: Medium

- Code Smell Type: Violation of Single Responsibility Principle (SRP)
- Problem Location: `get_items()` function.
- Detailed Explanation: The route handler is responsible for both the HTTP request/response logic and the business logic of filtering and transforming the data based on `CONFIG`. As the transformation rules grow, this function will become bloated.
- Improvement Suggestions: Extract the data transformation logic into a separate service function (e.g., `format_items(data, config)`) that can be unit tested independently of the Flask request context.
- Priority Level: Low