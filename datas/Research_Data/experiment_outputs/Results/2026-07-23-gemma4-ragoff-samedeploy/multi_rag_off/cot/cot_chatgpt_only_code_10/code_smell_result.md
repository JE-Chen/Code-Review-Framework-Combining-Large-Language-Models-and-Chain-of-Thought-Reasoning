- Code Smell Type: Mutable Default Argument
- Problem Location: `def fetch_resource(url, headers={}, ...):`
- Detailed Explanation: In Python, default arguments are evaluated once at definition time, not at execution time. Because `headers` is a dictionary (mutable), any modification to it (like `headers["User-Agent"] = "BadClient/1.0"`) persists across all subsequent calls to the function. This leads to unpredictable behavior where headers from a previous call leak into the next.
- Improvement Suggestions: Use `headers=None` as the default value and initialize it inside the function: `headers = headers if headers is not None else {}`.
- Priority Level: High

- Code Smell Type: Shadowing Built-in Function
- Problem Location: `def hash(text):`
- Detailed Explanation: `hash()` is a built-in Python function used to get the hash value of an object. By defining a custom function named `hash`, the built-in functionality is overwritten within this module's scope, which can lead to confusion and bugs if the original `hash()` is needed.
- Improvement Suggestions: Rename the function to something more descriptive, such as `calculate_md5` or `get_checksum`.
- Priority Level: Medium

- Code Smell Type: Improper State Management (Function Attribute as Cache)
- Problem Location: `if not hasattr(fetch_resource, "cache"): fetch_resource.cache = {}`
- Detailed Explanation: Using a function attribute to store a cache is a non-standard pattern that makes the code harder to test and maintain. It creates a hidden global state that is difficult to clear or configure, and it is not thread-safe.
- Improvement Suggestions: Use a dedicated cache class, a global dictionary (if appropriate), or a standard decorator like `functools.lru_cache`.
- Priority Level: Medium

- Code Smell Type: Inefficient String Concatenation
- Problem Location: `line = r["url"] + " | " + str(r["status"]) + ...` in `print_summary`
- Detailed Explanation: Using the `+` operator for multiple string concatenations is less efficient and less readable than modern Python formatting methods.
- Improvement Suggestions: Use f-strings: `line = f"{r['url']} | {r['status']} | {r['server']} | {r['size']}"`.
- Priority Level: Low

- Code Smell Type: Magic Number
- Problem Location: `for chunk in resp.iter_content(chunk_size=1234):`
- Detailed Explanation: The value `1234` is an arbitrary number without a clear explanation of why this specific size was chosen. This makes the code less maintainable.
- Improvement Suggestions: Define a constant at the top of the file, e.g., `CHUNK_SIZE = 1024`, to provide semantic meaning.
- Priority Level: Low