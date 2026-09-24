- Code Smell Type: Duplicate Code (Boilerplate)
- Problem Location: `get_users`, `get_posts`, and `get_todos` functions.
- Detailed Explanation: These three functions are nearly identical, differing only by the endpoint string and the cache key. This violates the DRY (Don't Repeat Yourself) principle. If the caching logic or the way the client is called needs to change, it must be updated in three separate places, increasing the risk of inconsistency and maintenance overhead.
- Improvement Suggestions: Create a generic helper function, e.g., `fetch_and_cache(client, endpoint, cache_key)`, or integrate the caching logic directly into the `APIClient` class.
- Priority Level: Medium

- Code Smell Type: Global State / Tight Coupling
- Problem Location: `GLOBAL_CACHE = {}` and its usage inside `get_users`, `get_posts`, and `get_todos`.
- Detailed Explanation: The use of a global dictionary for caching makes the code harder to test and reason about. It introduces hidden dependencies between functions and makes the code thread-unsafe. It also prevents the application from having multiple independent cache instances if needed in the future.
- Improvement Suggestions: Encapsulate the cache within the `APIClient` class or pass a cache object as a dependency to the functions.
- Priority Level: Medium

- Code Smell Type: Poor Error Handling (Swallowing Exceptions)
- Problem Location: `APIClient.fetch` method (`except Exception as e: return {"error": str(e)}`).
- Detailed Explanation: Catching the base `Exception` class and returning it as a dictionary value is a dangerous pattern. It masks the type of error (e.g., ConnectionError vs. Timeout) and forces the caller to check for the presence of an `"error"` key in the return value rather than handling specific exceptions. This leads to fragile logic in `process_all`, which assumes the returned value is always a list.
- Improvement Suggestions: Catch specific `requests` exceptions (e.g., `RequestException`). Allow exceptions to propagate to the caller or use a dedicated Result/Either pattern. Ensure the return type is consistent (e.g., always a list or raise an exception).
- Priority Level: High

- Code Smell Type: Deeply Nested Conditionals (Arrow Anti-pattern)
- Problem Location: `main()` function, specifically the `if len(results) > 0` block.
- Detailed Explanation: The nested `if/else` structure for categorizing the number of results is unnecessarily deep. This reduces readability and makes the logic harder to follow as the number of conditions grows.
- Improvement Suggestions: Use "guard clauses" to return early or use a flatter `if/elif/else` structure.
- Priority Level: Low