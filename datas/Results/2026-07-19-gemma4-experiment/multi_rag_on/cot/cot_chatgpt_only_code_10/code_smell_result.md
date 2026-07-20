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

- Code Smell Type: Shadowing Built-in Function
- Problem Location: `def hash(text):`
- Detailed Explanation: `hash()` is a built-in Python function used to get the hash value of an object. By defining a custom function named `hash`, the built-in functionality is shadowed (overwritten) within the module's scope. This can lead to confusion for other developers and potential bugs if the built-in `hash()` is needed elsewhere.
- Improvement Suggestions: Rename the function to something more descriptive, such as `calculate_md5` or `generate_checksum`.
- Priority Level: Medium

---

- Code Smell Type: Function Attribute as State (Poor Encapsulation)
- Problem Location: `if not hasattr(fetch_resource, "cache"): fetch_resource.cache = {}`
- Detailed Explanation: Using a function attribute to implement a cache is a non-standard pattern that mimics a static variable. It makes the code harder to test (as the cache persists between test cases) and violates the principle of separation of concerns. It is an unconventional way to manage state that reduces readability.
- Improvement Suggestions: Use a dedicated cache object, a class with a method, or the standard library's `functools.lru_cache` decorator for a more idiomatic and maintainable approach.
- Priority Level: Medium

---

- Code Smell Type: Inefficient String Concatenation
- Problem Location: `line = r["url"] + " | " + str(r["status"]) + ...` inside `print_summary`
- Detailed Explanation: Using the `+` operator for multiple string concatenations is less efficient and less readable than modern Python formatting. It requires explicit type casting (e.g., `str(r["status"])`), which clutters the logic.
- Improvement Suggestions: Use f-strings (available in Python 3.6+) for better readability and performance:
  ```python
  line = f"{r['url']} | {r['status']} | {r['server']} | {r['size']}"
  ```
- Priority Level: Low