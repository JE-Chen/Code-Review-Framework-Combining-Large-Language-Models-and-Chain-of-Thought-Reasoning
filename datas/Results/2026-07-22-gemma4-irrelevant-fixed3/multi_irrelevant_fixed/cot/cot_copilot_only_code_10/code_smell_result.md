- Code Smell Type: Duplicate Code / Lack of Abstraction
- Problem Location: `get_users`, `get_posts`, and `get_todos` functions.
- Detailed Explanation: These three functions are nearly identical, differing only by the endpoint string and the cache key. This violates the DRY (Don't Repeat Yourself) principle. If the caching logic or the way data is fetched needs to change, it must be updated in three separate places, increasing the risk of inconsistency and maintenance overhead.
- Improvement Suggestions: Create a generic `fetch_and_cache(client, endpoint, cache_key)` function that handles the fetching and caching logic, and call this helper from the specific functions or replace them entirely.
- Priority Level: Medium

- Code Smell Type: Global State / Tight Coupling
- Problem Location: `GLOBAL_CACHE = {}` and its usage in `get_users`, `get_posts`, and `get_todos`.
- Detailed Explanation: The use of a global dictionary for caching makes the code harder to test and reason about. It introduces hidden dependencies between functions and makes the system non-thread-safe. It also prevents the creation of multiple `APIClient` instances with independent caches.
- Improvement Suggestions: Move the cache into the `APIClient` class as an instance attribute (e.g., `self.cache = {}`) or pass a cache object as a dependency to the functions.
- Priority Level: High

- Code Smell Type: Poor Error Handling (Swallowing Exceptions)
- Problem Location: `APIClient.fetch` method (`except Exception as e: return {"error": str(e)}`).
- Detailed Explanation: Catching the base `Exception` class and returning it as a dictionary value is a dangerous pattern. It masks the type of error (e.g., ConnectionError vs. Timeout) and forces the caller to check for an `"error"` key in the return value rather than handling specific exceptions. This leads to fragile code where errors can propagate silently until they cause a crash elsewhere.
- Improvement Suggestions: Catch specific exceptions (e.g., `requests.RequestException`). Instead of returning a dictionary with an error string, allow exceptions to bubble up to the caller or raise a custom domain-specific exception.
- Priority Level: High

- Code Smell Type: Deeply Nested Conditionals (Arrow Anti-pattern)
- Problem Location: `main()` function, specifically the `if len(results) > 0` block.
- Detailed Explanation: The nested `if/else` structure for categorizing the number of results is unnecessarily deep. This reduces readability and makes the logic harder to follow as the number of conditions grows.
- Improvement Suggestions: Use "guard clauses" to handle the empty case early and return/exit, or use a more linear `if/elif/else` structure to flatten the logic.
- Priority Level: Low