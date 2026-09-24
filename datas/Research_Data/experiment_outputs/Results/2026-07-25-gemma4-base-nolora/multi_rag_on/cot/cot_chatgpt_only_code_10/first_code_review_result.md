### Code Review

**1. Readability & Consistency**
* **String Formatting:** In `print_summary`, the use of string concatenation (`+`) is outdated and harder to read. Suggest using f-strings for better clarity.
* **Naming:** The variable `r` is used throughout the codebase. While common for "response," using `response` would improve semantic clarity.

**2. Naming Conventions**
* **Shadowing Built-ins:** The function `hash(text)` shadows the Python built-in `hash()` function. This should be renamed to `calculate_hash` or `get_md5_hash` to avoid conflicts and confusion.

**3. Software Engineering Standards**
* **Mutable Default Arguments:** In `fetch_resource(url, headers={}, ...)`, the `headers` dictionary is a mutable default argument. Since the function modifies it (`headers["User-Agent"] = ...`), these changes will persist across subsequent calls to the function, leading to unexpected behavior. Use `headers=None` and initialize inside the function.
* **State Management:** Using a function attribute (`fetch_resource.cache`) as a makeshift cache is unconventional. Consider using a class or a dedicated cache decorator (e.g., `functools.lru_cache`).
* **Single Responsibility:** `download_file` handles both the network request and the file system I/O. These should be split into two functions to improve testability.

**4. Logic & Correctness**
* **Memory Efficiency:** In `download_file`, the code iterates through chunks but appends them all to a bytes object (`content += chunk`) before writing to a file. This defeats the purpose of `stream=True` and will cause a `MemoryError` for large files. Write chunks directly to the file inside the loop.
* **Error Handling:** There is a complete lack of exception handling (e.g., `try...except` blocks) for network requests. A single connection failure will crash the entire batch process.

**5. Performance & Security**
* **Hashing Algorithm:** `hashlib.md5` is used. While acceptable for simple checksums, it is cryptographically broken. If this is used for security/integrity verification, consider `sha256`.

**6. Summary of Suggested Improvements**
* Change `headers={}` to `headers=None`.
* Rename `hash()` to `calculate_md5()`.
* Update `download_file` to write chunks directly to disk: `f.write(chunk)`.
* Replace string concatenation in `print_summary` with f-strings.
* Wrap `requests.get` calls in `try...except` blocks to handle `RequestException`.