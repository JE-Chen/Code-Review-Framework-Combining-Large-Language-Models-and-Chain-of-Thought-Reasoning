- Code Smell Type: Mutable Default Argument
- Problem Location: `def fetch_resource(url, headers={}, ...):`
- Detailed Explanation: In Python, default arguments are evaluated once at definition time. Because `headers` is a dictionary (mutable), any modification to it (like `headers["User-Agent"] = "BadClient/1.0"`) persists across all subsequent calls to the function that rely on the default value. This creates hidden shared state and unpredictable behavior.
- Improvement Suggestions: Set the default value to `None` and initialize the dictionary inside the function: `if headers is None: headers = {}`.
- Priority Level: High

- Code Smell Type: Shared Mutable State (Function Attribute as Cache)
- Problem Location: `if not hasattr(fetch_resource, "cache"): fetch_resource.cache = {}`
- Detailed Explanation: Using a function attribute to implement a cache creates a global-like mutable state. This makes the code difficult to test (tests will interfere with each other), prevents thread safety, and makes the cache lifecycle impossible to manage explicitly.
- Improvement Suggestions: Use a dedicated cache object, a class to encapsulate the fetcher and its state, or a standard decorator like `functools.lru_cache`.
- Priority Level: Medium

- Code Smell Type: Modifying Input Arguments
- Problem Location: `headers["User-Agent"] = "BadClient/1.0"` inside `fetch_resource`.
- Detailed Explanation: The function modifies the `headers` dictionary passed by the caller. If the caller intends to reuse that dictionary for other requests, they will find their `User-Agent` has been unexpectedly changed, leading to side effects in other parts of the application.
- Improvement Suggestions: Create a shallow copy of the headers before modifying them: `current_headers = headers.copy()`.
- Priority Level: Medium

- Code Smell Type: Magic Numbers
- Problem Location: `chunk_size=1234` and `len(content) > 3000` in `download_file`.
- Detailed Explanation: Hard-coded numeric literals lack semantic meaning. It is unclear why `1234` was chosen as a chunk size or why `3000` is the threshold for a preview. This makes maintenance difficult.
- Improvement Suggestions: Define these as named constants at the top of the module (e.g., `DEFAULT_CHUNK_SIZE = 1024`, `PREVIEW_MAX_BYTES = 3000`).
- Priority Level: Low

- Code Smell Type: Shadowing Built-in Function
- Problem Location: `def hash(text):`
- Detailed Explanation: `hash` is a built-in Python function. Redefining it as a custom function shadows the original, which can lead to confusion and bugs if the built-in `hash()` is needed elsewhere in the module or by libraries.
- Improvement Suggestions: Rename the function to something more descriptive, such as `calculate_md5_hash`.
- Priority Level: Low