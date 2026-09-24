- Code Smell Type: Mutable Default Argument
- Problem Location: `def fetch_resource(url, headers={}, ...):`
- Detailed Explanation: In Python, default arguments are evaluated once at definition time, not at execution time. Because `headers` is a dictionary (mutable), any modification made to it inside the function (e.g., `headers["User-Agent"] = "BadClient/1.0"`) persists across subsequent calls to the function. This leads to unpredictable behavior and side effects where headers from one request leak into another.
- Improvement Suggestions: Use `None` as the default value and initialize the dictionary inside the function:
  ```python
  def fetch_resource(url, headers=None, ...):
      if headers is None:
          headers = {}
  ```
- Priority Level: High

---

- Code Smell Type: Violation of Single Responsibility Principle (SRP) / State Management
- Problem Location: `fetch_resource` function (specifically the `hasattr(fetch_resource, "cache")` block).
- Detailed Explanation: The function is responsible for both fetching resources and managing a global cache state. Attaching a cache to the function object itself is a non-standard pattern that makes the code harder to test (cache persists between tests) and maintain. It mixes I/O logic with state management.
- Improvement Suggestions: Extract the caching logic into a separate class or use a dedicated caching decorator/library (like `functools.lru_cache`). If a manual cache is needed, pass a cache object as a dependency to the function.
- Priority Level: Medium

---

- Code Smell Type: Shadowing Built-in Function
- Problem Location: `def hash(text):`
- Detailed Explanation: `hash` is a built-in Python function used to get the hash value of an object. By naming a custom function `hash`, the built-in functionality is shadowed within the module's scope. This can lead to confusion for other developers and potential bugs if the built-in `hash()` is needed.
- Improvement Suggestions: Rename the function to something more descriptive, such as `calculate_md5` or `get_checksum`.
- Priority Level: Low

---

- Code Smell Type: Inefficient Resource Handling / Memory Risk
- Problem Location: `download_file` function (the `content += chunk` loop).
- Detailed Explanation: The code reads chunks from a stream but concatenates them into a byte string (`content`) in memory before writing to a file. This defeats the purpose of using `stream=True` and `iter_content`. If a very large file is downloaded, the program will consume excessive RAM and potentially crash with a `MemoryError`.
- Improvement Suggestions: Write chunks directly to the file inside the loop:
  ```python
  with open(path, "wb") as f:
      for chunk in resp.iter_content(chunk_size=1234):
          if preview and f.tell() > 3000:
              break
          f.write(chunk)
  ```
- Priority Level: High