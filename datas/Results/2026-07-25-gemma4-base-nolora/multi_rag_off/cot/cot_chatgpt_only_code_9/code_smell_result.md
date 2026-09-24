- Code Smell Type: Duplicate Code (Dry Principle Violation)
- Problem Location: `get_users(client)`, `get_posts(client)`, and `get_todos(client)`
- Detailed Explanation: These three functions are identical in logic, differing only by the endpoint string and the cache key. This repetition increases maintenance effort; if the caching logic or the way `client.fetch` is called needs to change, it must be updated in three separate places.
- Improvement Suggestions: Create a generic helper function, e.g., `fetch_and_cache(client, endpoint, cache_key)`, or integrate the caching mechanism directly into the `APIClient` class.
- Priority Level: Medium

- Code Smell Type: Tight Coupling / Global State Dependency
- Problem Location: `GLOBAL_CACHE = {}` and its usage inside `get_users`, `get_posts`, and `get_todos`.
- Detailed Explanation: The functions rely on a global variable for state management. This makes the code difficult to test in isolation (unit tests will share state), prevents thread safety, and makes it harder to track where and when the cache is being modified.
- Improvement Suggestions: Encapsulate the cache within the `APIClient` class as an instance attribute or pass a cache object as a dependency to the functions.
- Priority Level: High

- Code Smell Type: Poor Error Handling (Silent Failures)
- Problem Location: `APIClient.fetch` method's `try...except` and `else` blocks.
- Detailed Explanation: The method catches all exceptions and returns a dictionary containing an `"error"` key instead of raising an exception. This forces every calling function (like `get_users`) to manually check if the returned data is a list of results or an error dictionary. In `process_all()`, the code iterates over `users`, `posts`, and `todos` assuming they are lists; if an error occurs, the code will crash with a `TypeError` when trying to iterate over the error dictionary.
- Improvement Suggestions: Allow exceptions to propagate or raise custom exceptions. Use `response.raise_for_status()` to handle HTTP errors properly.
- Priority Level: High

- Code Smell Type: Deeply Nested Conditionals (Arrow Anti-pattern)
- Problem Location: `main()` function, specifically the `if len(results) > 0` block.
- Detailed Explanation: The nested `if/else` structure for categorizing the number of results reduces readability. As more categories are added, the indentation will continue to shift right, making the logic harder to follow.
- Improvement Suggestions: Use "guard clauses" to return early or use a flatter `if/elif/else` structure.
- Priority Level: Low