- Code Smell Type: Mutable Default Argument
- Problem Location: `def fetch_resource(url, headers={}, ...):`
- Detailed Explanation: In Python, default arguments are evaluated once at definition time, not at execution time. Because `headers` is a dictionary (mutable), any modification made to it inside the function (e.g., `headers["User-Agent"] = "BadClient/1.0"`) persists across subsequent calls to the function. This leads to unexpected side effects where headers from one request leak into another.
- Improvement Suggestions: Use `None` as the default value and initialize the dictionary inside the function:
  ```python
  def fetch_resource(url, headers=None, ...):
      if headers is None:
          headers = {}
  ```
- Priority Level: High

- Code Smell Type: Shadowing Built-in Function
- Problem Location: `def hash(text):`
- Detailed Explanation: `hash()` is a built-in Python function used to get the hash value of an object. By defining a custom function named `hash`, the built-in functionality is shadowed (overwritten) within the module's scope. This can lead to confusion for other developers and potential bugs if the built-in `hash()` is needed.
- Improvement Suggestions: Rename the function to something more descriptive, such as `calculate_md5` or `generate_checksum`.
- Priority Level: Medium

- Code Smell Type: Improper State Management (Function Attribute as Cache)
- Problem Location: `if not hasattr(fetch_resource, "cache"): fetch_resource.cache = {}`
- Detailed Explanation: Using a function attribute to implement a cache is a non-standard pattern that makes the code harder to test and maintain. It creates a hidden global state attached to the function object. This makes it difficult to clear the cache between unit tests or to implement cache expiration/size limits.
- Improvement Suggestions: Use a dedicated cache class, a global dictionary (if simple), or the standard library's `functools.lru_cache` decorator for a more idiomatic approach.
- Priority Level: Medium

- Code Smell Type: Inefficient String Concatenation in Loop
- Problem Location: `content += chunk` inside `download_file`
- Detailed Explanation: In Python, strings and bytes are immutable. Using `+=` in a loop creates a new copy of the entire content buffer every time a chunk is added. For large files, this results in quadratic time complexity $O(n^2)$ and excessive memory allocation.
- Improvement Suggestions: Collect chunks in a list and join them at the end, or write the chunks directly to the file object within the loop:
  ```python
  with open(path, "wb") as f:
      for chunk in resp.iter_content(chunk_size=1234):
          f.write(chunk)
          if preview and f.tell() > 3000:
              break
  ```
- Priority Level: Medium

- Code Smell Type: Magic Numbers
- Problem Location: `chunk_size=1234` and `len(content) > 3000`
- Detailed Explanation: The numbers `1234` and `3000` are "magic numbers"—hardcoded values without explanation. It is unclear why these specific values were chosen, making the code less maintainable.
- Improvement Suggestions: Define these as named constants at the top of the module (e.g., `CHUNK_SIZE_BYTES = 1024`, `PREVIEW_LIMIT_BYTES = 3000`).
- Priority Level: Low