- Code Smell Type: Duplicate Code (Boilerplate)
- Problem Location: `get_users`, `get_posts`, and `get_todos` functions.
- Detailed Explanation: These three functions perform identical logic: calling `client.fetch` with a specific endpoint and updating a global cache. This violates the DRY (Don't Repeat Yourself) principle, making the code harder to maintain. If the caching logic changes, it must be updated in three different places.
- Improvement Suggestions: Create a generic `get_resource(client, resource_name)` function that takes the endpoint/key as an argument.
- Priority Level: Medium

- Code Smell Type: Global State / Tight Coupling
- Problem Location: `GLOBAL_CACHE = {}` and its usage inside `get_users`, `get_posts`, and `get_todos`.
- Detailed Explanation: The use of a global dictionary for caching creates hidden dependencies and makes the code difficult to test in isolation. It can lead to unpredictable behavior in multi-threaded environments or when running multiple test cases, as state persists between calls.
- Improvement Suggestions: Move the cache into the `APIClient` class as an instance attribute or pass a cache object explicitly to the functions.
- Priority Level: High

- Code Smell Type: Poor Error Handling (Swallowing Exceptions)
- Problem Location: `APIClient.fetch` method (`except Exception as e: return {"error": str(e)}`).
- Detailed Explanation: Catching the base `Exception` class and returning it as a dictionary value masks the type of error (e.g., ConnectionError vs. Timeout). Furthermore, the calling functions (`get_users`, etc.) do not check if the returned data is an error dictionary or a list of results before proceeding, which will cause the `process_all` loops to crash or behave unexpectedly when an error occurs.
- Improvement Suggestions: Use specific exception handling (e.g., `requests.exceptions.RequestException`). Either raise the exception to be handled by the caller or return a consistent Response object/tuple that explicitly separates data from errors.
- Priority Level: High

- Code Smell Type: Deeply Nested Conditionals (Arrow Anti-pattern)
- Problem Location: `main()` function, specifically the `if len(results) > 0` block.
- Detailed Explanation: The nested `if/else` structure for categorizing the number of results reduces readability. As more categories are added, the indentation will continue to shift right, making the logic harder to follow.
- Improvement Suggestions: Use "guard clauses" to return early or use a flatter `if/elif/else` structure.
- Priority Level: Low