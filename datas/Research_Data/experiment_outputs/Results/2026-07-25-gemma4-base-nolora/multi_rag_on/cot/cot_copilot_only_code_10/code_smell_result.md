- Code Smell Type: Tight Coupling / Global State Dependency
- Problem Location: `GLOBAL_CACHE = {}` and its usage in `get_users`, `get_posts`, and `get_todos`.
- Detailed Explanation: The functions `get_users`, `get_posts`, and `get_todos` rely on and modify a global variable (`GLOBAL_CACHE`). This creates hidden dependencies, making the code difficult to test in isolation (unit tests will leak state between each other) and potentially causing race conditions if the code ever becomes multi-threaded.
- Improvement Suggestions: Pass a cache object as an optional argument to the functions or, preferably, encapsulate the cache within the `APIClient` class to maintain state locally.
- Priority Level: High

- Code Smell Type: Duplicate Code (Boilerplate)
- Problem Location: 
  ```python
  def get_users(client):
      data = client.fetch("/users")
      GLOBAL_CACHE["users"] = data
      return data
  # ... repeated for get_posts and get_todos
  ```
- Detailed Explanation: The three getter functions are identical in logic, differing only by the endpoint string and the cache key. This violates the DRY (Don't Repeat Yourself) principle, increasing maintenance effort if the fetching or caching logic needs to change.
- Improvement Suggestions: Create a generic `get_resource(client, endpoint)` function that handles the fetching and caching dynamically.
- Priority Level: Medium

- Code Smell Type: Poor Error Handling (Silent Failures)
- Problem Location: `APIClient.fetch` method.
- Detailed Explanation: The method catches all exceptions (`Exception as e`) and returns a dictionary containing an error string. This forces the caller to check if the returned data is a list/object or an error dictionary. If the caller forgets to check (as seen in `process_all`), the code will crash with a `TypeError` when trying to iterate over the error dictionary (e.g., `for u in users:` where `users` is `{"error": "..."}`).
- Improvement Suggestions: Raise custom exceptions for API failures. Let the caller decide how to handle the error or use a consistent response wrapper/Result type.
- Priority Level: High

- Code Smell Type: Deeply Nested Conditionals (Arrow Anti-pattern)
- Problem Location: `main()` function's result count logic.
- Detailed Explanation: The nested `if/else` blocks for checking the length of `results` reduce readability and increase cognitive load. This structure is unnecessary for simple range checks.
- Improvement Suggestions: Use a "guard clause" to handle the empty list case first, then use `elif` statements to flatten the logic.
- Priority Level: Low