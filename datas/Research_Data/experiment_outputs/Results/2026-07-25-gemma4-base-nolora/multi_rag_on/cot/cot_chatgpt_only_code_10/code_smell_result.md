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

- Code Smell Type: Violation of Single Responsibility Principle (SRP) / State Management
- Problem Location: `fetch_resource` function (specifically the `hasattr(fetch_resource, "cache")` block).
- Detailed Explanation: The function is responsible for both fetching resources and managing a global cache state by attaching a dictionary to the function object itself. This is a non-standard way of implementing a cache, making the code harder to test (cache persists between tests) and preventing the use of different cache instances for different purposes.
- Improvement Suggestions: Move the cache to a separate class (e.g., a `ResourceFetcher` class) or use a dedicated caching decorator like `functools.lru_cache`.
- Priority Level: Medium

- Code Smell Type: Shadowing Built-in Function
- Problem Location: `def hash(text):`
- Detailed Explanation: `hash()` is a built-in Python function used to get the hash value of an object. By naming a custom function `hash`, the built-in functionality is shadowed (overwritten) within the module's scope. This can lead to confusion for other developers and potential bugs if the built-in `hash()` is needed.
- Improvement Suggestions: Rename the function to something more descriptive, such as `calculate_md5` or `get_checksum`.
- Priority Level: Medium

- Code Smell Type: Inefficient Resource Handling (Memory Exhaustion Risk)
- Problem Location: `download_file` function, specifically `content += chunk`.
- Detailed Explanation: The code uses `stream=True` to fetch the file in chunks, but then concatenates these chunks into a byte string (`content`) in memory before writing to a file. For large files, this defeats the purpose of streaming and can lead to a `MemoryError` as the entire file is loaded into RAM.
- Improvement Suggestions: Write the chunks directly to the file inside the loop:
  ```python
  with open(path, "wb") as f:
      for chunk in resp.iter_content(chunk_size=1234):
          if preview and f.tell() > 3000:
              break
          f.write(chunk)
  ```
- Priority Level: High

- Code Smell Type: Lack of Error Handling
- Problem Location: `requests.get(...)` calls in `fetch_resource`, `download_file`, and `wait_until_ready`.
- Detailed Explanation: The code assumes network requests will always succeed. It does not use `r.raise_for_status()` or wrap calls in `try...except` blocks. Any network timeout, DNS failure, or 5xx server error will cause the entire program to crash.
- Improvement Suggestions: Wrap network calls in `try...except requests.exceptions.RequestException` blocks and use `r.raise_for_status()` to handle HTTP error codes.
- Priority Level: High