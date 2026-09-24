### Code Review

**1. Readability & Consistency**
* **String Formatting:** In `print_summary`, the use of string concatenation (`+`) is outdated and harder to read. Use f-strings for better clarity.
* **Naming:** The function name `hash()` shadows the Python built-in `hash()` function. Rename it to something more specific, like `calculate_md5`.

**2. Software Engineering Standards**
* **Mutable Default Arguments:** In `fetch_resource(url, headers={}, ...)`, the `headers` dictionary is a mutable default argument. This can lead to unexpected behavior across function calls. Use `headers=None` and initialize inside the function.
* **State Management:** Using a function attribute (`fetch_resource.cache`) as a cache is unconventional. Consider using a class or a dedicated cache decorator (e.g., `functools.lru_cache`).
* **Single Responsibility:** `download_file` handles both the network request and the file system I/O. These should be separated to improve testability.

**3. Logic & Correctness**
* **Resource Leak:** In `download_file`, the `requests.get(url, stream=True)` call is not wrapped in a `with` statement or explicitly closed, which can lead to leaked connections.
* **Inefficient Buffer:** In `download_file`, `content += chunk` creates a new bytes object in every iteration. For large files, this is highly inefficient. Write chunks directly to the file instead of accumulating them in memory.

**4. Performance & Security**
* **MD5 Usage:** `hashlib.md5` is used for checksums. While acceptable for integrity checks, ensure it is not used for security-sensitive hashing.

**5. Summary of Suggestions**
* Change `headers={}` to `headers=None`.
* Rename `hash()` to `calculate_md5()`.
* Use `with requests.get(...) as resp:` in `download_file`.
* Write chunks directly to the file in `download_file` instead of using a `content` variable.
* Replace string concatenation in `print_summary` with f-strings.