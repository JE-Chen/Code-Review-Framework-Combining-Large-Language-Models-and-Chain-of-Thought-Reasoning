### Code Review

#### 1. Readability & Consistency
- **Formatting**: The code generally follows PEP 8 spacing and indentation.
- **String Concatenation**: In `print_summary`, the use of `+` for string concatenation is outdated. Recommend using f-strings for better readability and performance.

#### 2. Naming Conventions
- **Shadowing Built-ins**: The function `hash(text)` shadows the Python built-in `hash()` function. This is a significant naming conflict and should be renamed to something like `calculate_md5` or `get_checksum`.

#### 3. Software Engineering Standards
- **State Management**: `fetch_resource` uses a function attribute (`fetch_resource.cache`) to store state. This is an unconventional pattern that makes the code harder to test and reason about. Recommend using a class with a cache instance or a dedicated cache object.
- **Modularization**: The `download_file` function reads the entire file into memory (`content += chunk`) before writing to disk. This defeats the purpose of `stream=True` and `iter_content`.

#### 4. Logic & Correctness
- **Mutable Default Arguments**: In `fetch_resource(url, headers={}, ...)`, the `headers` dictionary is a mutable default argument. Since dictionaries are created once at definition time, modifications to `headers` (like adding the User-Agent) will persist across different function calls, leading to unexpected behavior.
- **Resource Leak**: In `download_file`, the `requests.get` response object is not closed. Use a `with` statement: `with requests.get(url, stream=True) as resp:`.
- **Error Handling**: There is a complete lack of exception handling (e.g., `try...except` blocks) for network requests. `requests.get` can throw `ConnectionError`, `Timeout`, or `HTTPError`, which would crash the program.

#### 5. Performance & Security
- **Memory Efficiency**: In `download_file`, the `content` variable grows linearly with file size. For large files, this will cause an `OutOfMemory` error. Write chunks directly to the file:
  ```python
  with open(path, "wb") as f:
      for chunk in resp.iter_content(chunk_size=1234):
          f.write(chunk)
  ```
- **Security**: The code uses `MD5` for checksums. While acceptable for basic integrity checks, MD5 is cryptographically broken. If this is used for security-sensitive verification, upgrade to `SHA-256`.

#### 6. Documentation & Testing
- **Missing Documentation**: None of the functions have docstrings explaining their parameters or return types.
- **Testing**: No unit tests are provided for the logic (especially the caching and batching logic).

---

### Summary of Recommendations

| Severity | Issue | Recommendation |
| :--- | :--- | :--- |
| **High** | Mutable Default Argument | Change `headers={}` to `headers=None` and initialize inside the function. |
| **High** | Memory Leak/Inefficiency | Write chunks directly to disk in `download_file` instead of accumulating in a byte string. |
| **Medium** | Shadowing Built-in | Rename `hash()` to `calculate_checksum()`. |
| **Medium** | State Management | Move the cache from a function attribute to a class or a separate dictionary. |
| **Medium** | Error Handling | Wrap network calls in `try...except` blocks. |
| **Low** | String Formatting | Replace `+` concatenation with f-strings in `print_summary`. |