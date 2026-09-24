- Code Smell Type: Shared Mutable State
- Problem Location: `GLOBAL_CACHE = {}` and its usage in `get_users`, `get_posts`, and `get_todos`.
- Detailed Explanation: The use of a global dictionary to cache API responses introduces hidden coupling between functions. This makes the code difficult to test in isolation (as state persists between tests) and can lead to unpredictable behavior in multi-threaded environments or when the application grows.
- Improvement Suggestions: Encapsulate the cache within the `APIClient` class or a dedicated `CacheManager` object and pass it explicitly to the functions that require it.
- Priority Level: High

- Code Smell Type: Inconsistent Return Types
- Problem Location: `APIClient.fetch` method.
- Detailed Explanation: The function returns a successful JSON response (likely a list or dict) on success, but returns a dictionary with an `"error"` key on failure. This forces every caller to check for the existence of an "error" key before processing data, increasing the risk of `TypeError` or `KeyError` if the caller assumes the data is a list.
- Improvement Suggestions: Raise custom exceptions for API errors (e.g., `APIError`) and let the caller handle them, or return a consistent Result object/tuple (e.g., `(data, error)`).
- Priority Level: High

- Code Smell Type: Broad Exception Handling
- Problem Location: `except Exception as e:` in `APIClient.fetch`.
- Detailed Explanation: Catching the base `Exception` class hides unexpected bugs (like `KeyboardInterrupt` or `NameError`) and makes debugging difficult. It treats all failures—from network timeouts to coding errors—identically.
- Improvement Suggestions: Catch specific exceptions provided by the `requests` library, such as `requests.exceptions.RequestException`.
- Priority Level: Medium

- Code Smell Type: Deeply Nested Conditional Logic
- Problem Location: `main()` function, specifically the `if len(results) > 0:` block.
- Detailed Explanation: The nested `if/else` structure for categorizing the number of results increases cognitive load and reduces readability.
- Improvement Suggestions: Use guard clauses or a flatter structure. Since these are mutually exclusive ranges, a series of `if/elif/else` statements would be much cleaner.
- Priority Level: Low

- Code Smell Type: Duplicate Code / Lack of Abstraction
- Problem Location: `get_users`, `get_posts`, and `get_todos` functions.
- Detailed Explanation: These three functions are nearly identical, differing only by the endpoint string and the cache key. This violates the DRY (Don't Repeat Yourself) principle.
- Improvement Suggestions: Create a single generic function `get_resource(client, endpoint)` that handles fetching and caching based on the provided endpoint.
- Priority Level: Low