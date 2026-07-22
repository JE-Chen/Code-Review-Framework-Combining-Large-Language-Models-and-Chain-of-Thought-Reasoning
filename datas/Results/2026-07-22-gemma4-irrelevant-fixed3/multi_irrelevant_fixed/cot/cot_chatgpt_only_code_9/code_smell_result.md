- Code Smell Type: Duplicate Code / Lack of Abstraction
- Problem Location: `get_users`, `get_posts`, and `get_todos` functions.
- Detailed Explanation: These three functions are nearly identical, differing only by the endpoint string and the cache key. This violates the DRY (Don't Repeat Yourself) principle. If the caching logic or the way data is fetched needs to change, it must be updated in three separate places, increasing the risk of inconsistency and maintenance overhead.
- Improvement Suggestions: Create a single generic function, e.g., `fetch_and_cache(client, endpoint, cache_key)`, and call it with the specific parameters for users, posts, and todos.
- Priority Level: Medium

- Code Smell Type: Global State / Tight Coupling
- Problem Location: `GLOBAL_CACHE = {}` and its usage inside `get_users`, `get_posts`, and `get_todos`.
- Detailed Explanation: The use of a global dictionary for caching creates hidden dependencies and makes the code difficult to test in isolation. It introduces side effects where calling a data-fetching function modifies a global variable, which can lead to unpredictable behavior in multi-threaded environments or during unit testing.
- Improvement Suggestions: Move the cache into the `APIClient` class as an instance attribute or pass a cache object as a dependency to the functions.
- Priority Level: High

- Code Smell Type: Poor Error Handling (Swallowing Exceptions)
- Problem Location: `APIClient.fetch` method (`except Exception as e: return {"error": str(e)}`).
- Detailed Explanation: Catching the base `Exception` class and returning it as a dictionary value masks the type of error (e.g., ConnectionError vs. Timeout) and forces the caller to check for an `"error"` key in the return value rather than handling specific exceptions. This makes the system fragile and harder to debug.
- Improvement Suggestions: Catch specific exceptions (e.g., `requests.RequestException`). Instead of returning a dictionary with an error string, allow exceptions to propagate or raise custom domain-specific exceptions that the caller can handle.
- Priority Level: High

- Code Smell Type: Deeply Nested Conditionals (Arrow Anti-pattern)
- Problem Location: `main()` function, specifically the `if len(results) > 0` block.
- Detailed Explanation: The nested `if/else` structure for categorizing the number of results is unnecessarily deep. This reduces readability and makes the logic harder to follow at a glance.
- Improvement Suggestions: Use a "guard clause" to handle the `len(results) == 0` case early and return/exit, or use a more flattened `if/elif/else` structure.
- Priority Level: Low