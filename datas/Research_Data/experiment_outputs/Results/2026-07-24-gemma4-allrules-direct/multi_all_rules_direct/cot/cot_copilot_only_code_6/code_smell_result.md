- Code Smell Type: Shared Mutable State
- Problem Location: `DATA_STORE = []`, `USER_COUNT = 0`, and the use of `global` keywords in `add_item` and `reset_data`.
- Detailed Explanation: Using global variables to store application state is dangerous in a web environment. Flask handles requests concurrently; since these globals are shared across all threads/processes, this will lead to race conditions and data corruption. Furthermore, it makes the code difficult to test in isolation.
- Improvement Suggestions: Use a proper database (e.g., PostgreSQL, SQLite) or a caching layer (e.g., Redis) to manage state. If a simple in-memory store is required for a prototype, encapsulate it within a class or a state management object.
- Priority Level: High

- Code Smell Type: Broad Exception Handling
- Problem Location: `except Exception as e:` in `add_item()`.
- Detailed Explanation: Catching the base `Exception` class hides unexpected bugs (like `TypeError` or `AttributeError`) and makes debugging difficult. It returns a generic error message to the user without distinguishing between client-side errors (e.g., missing JSON) and server-side crashes.
- Improvement Suggestions: Catch specific exceptions (e.g., `TypeError` if `request.json` is None) and implement a global error handler using `@app.errorhandler`.
- Priority Level: Medium

- Code Smell Type: Deeply Nested Conditional Logic
- Problem Location: `complex_route()` function.
- Detailed Explanation: The function uses multiple levels of nested `if/else` blocks. This increases cognitive load, makes the logic harder to follow, and increases the likelihood of bugs when adding new conditions.
- Improvement Suggestions: Use guard clauses to return early. For example, handle the `if not param` case first, then handle `isdigit()` and `param == "hello"` as separate top-level checks.
- Priority Level: Medium

- Code Smell Type: Violation of Single Responsibility Principle (SRP)
- Problem Location: `get_items()` function.
- Detailed Explanation: This function is responsible for both retrieving data and applying business logic/transformation rules based on the `CONFIG` state. As the transformation logic grows, this route handler will become bloated and untestable.
- Improvement Suggestions: Extract the item transformation logic into a separate helper function or a service layer (e.g., `transform_item(item, config)`).
- Priority Level: Low

- Code Smell Type: Lack of Input Validation
- Problem Location: `item = request.json.get("item")` in `add_item()`.
- Detailed Explanation: The code assumes `request.json` exists and that `item` is a string (since `get_items` calls `len()` and `.upper()` on it). If a user sends a non-string value or an empty body, the application will crash with a `TypeError` during the `get_items` call.
- Improvement Suggestions: Validate that the input is present and is of the expected type (string) before appending it to the data store.
- Priority Level: High