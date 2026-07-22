- Code Smell Type: Duplicate Code / Lack of Abstraction
- Problem Location: `get_users`, `get_posts`, and `get_todos` functions.
- Detailed Explanation: These three functions are nearly identical, differing only by the endpoint string and the cache key. This violates the DRY (Don't Repeat Yourself) principle. If the caching logic or the way the client is called needs to change, it must be updated in three separate places, increasing the risk of inconsistency and maintenance overhead.
- Improvement Suggestions: Create a generic `fetch_and_cache(client, endpoint, cache_key)` function or integrate the caching logic directly into the `APIClient` class.
- Priority Level: Medium

- Code Smell Type: Tight Coupling / Global State
- Problem Location: `GLOBAL_CACHE = {}` and its usage inside `get_users`, `get_posts`, and `get_todos`.
- Detailed Explanation: The functions rely on a global variable for state management. This makes the code difficult to test in isolation (unit tests will share state), prevents thread-safe execution, and makes it harder to track where and when the cache is being modified.
- Improvement Suggestions: Encapsulate the cache within the `APIClient` class or a dedicated `CacheManager` class and pass it as a dependency.
- Priority Level: High

- Code Smell Type: Poor Error Handling / Type Inconsistency
- Problem Location: `APIClient.fetch` method.
- Detailed Explanation: The method returns a dictionary containing an `"error"` key upon failure, but returns the actual JSON data (which could also be a dictionary) upon success. This forces the caller to check for the existence of an `"error"` key before processing data. Furthermore, `process_all` assumes the return value is always an iterable (list), which will cause a `TypeError` if `fetch` returns the error dictionary.
- Improvement Suggestions: Raise custom exceptions for API errors instead of returning error dictionaries. This allows the caller to handle failures using `try-except` blocks and ensures that a successful return value is always of the expected type.
- Priority Level: High

- Code Smell Type: Deeply Nested Conditionals (Arrow Anti-pattern)
- Problem Location: `main()` function, specifically the `if len(results) > 0` block.
- Detailed Explanation: The nested `if/else` structure for categorizing the number of results reduces readability. As more categories are added, the indentation will continue to shift right, making the logic harder to follow.
- Improvement Suggestions: Use a "guard clause" to handle the empty case first, then use a flat `if/elif/else` structure to categorize the results.
- Priority Level: Low