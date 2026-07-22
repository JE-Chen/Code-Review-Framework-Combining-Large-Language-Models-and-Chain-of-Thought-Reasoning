Here is the code review based on the provided global rules.

### 1. Readability & Consistency
- **String Formatting**: In `print_summary`, the code uses string concatenation (`+`). For better readability and performance, use f-strings (e.g., `f"{r['url']} | {r['status']}..."`).
- **Consistency**: The `fetch_resource` function uses a function attribute for caching, while other functions use standard local variables. This is an unconventional pattern in Python; a class or a dedicated cache object would be more consistent with standard practices.

### 2. Naming Conventions
- **Shadowing Built-ins**: The function `hash(text)` shadows the Python built-in `hash()` function. This is a high-risk naming choice that can lead to confusing bugs. Rename it to `calculate_checksum` or `get_md5_hash`.

### 3. Software Engineering Standards
- **Mutable Default Arguments**: In `fetch_resource(url, headers={}, ...)`, the `headers` dictionary is a mutable default argument. In Python, this dictionary is shared across all calls to the function. If one call modifies `headers`, those changes persist for subsequent calls.
    - *Fix*: Use `headers=None` and initialize inside the function: `if headers is None: headers = {}`.
- **Modularity**: The `fetch_resource` function handles both the network request and the caching logic. These should be separated to improve testability.

### 4. Logic & Correctness
- **Resource Leak**: In `download_file`, `requests.get(url, stream=True)` is called, but the response object is never closed. When using `stream=True`, it is critical to use a `with` statement or call `resp.close()` to avoid leaking connections.
- **Memory Inefficiency**: In `download_file`, the code iterates through chunks but appends them to a bytes object (`content += chunk`) before writing to a file. This defeats the purpose of streaming and will cause a `MemoryError` for large files.
    - *Fix*: Write chunks directly to the file inside the loop.
- **Error Handling**: There is a complete lack of `try...except` blocks around network calls (`requests.get`). Any DNS failure, timeout, or connection reset will crash the entire program.

### 5. Performance & Security
- **Security (Hashing)**: The code uses `MD5` for checksums. While acceptable for basic integrity checks, MD5 is cryptographically broken. If this is used for security verification, it should be upgraded to `SHA-256`.
- **Performance**: `batch_fetch` processes URLs sequentially. For a large list of URLs, this will be extremely slow. Consider using `concurrent.futures` or `asyncio`.

### 6. Documentation & Testing
- **Missing Documentation**: None of the functions have docstrings explaining their parameters or return types.
- **Testing**: No unit tests are provided for the logic (especially the caching and hashing logic).

---

### Summary of Major Issues
| Severity | Issue | Location |
| :--- | :--- | :--- |
| **Critical** | Mutable default argument `headers={}` | `fetch_resource` |
| **Critical** | Memory inefficiency/Streaming failure | `download_file` |
| **High** | Shadowing built-in `hash()` | `hash()` |
| **High** | Missing exception handling for I/O | All network calls |
| **Medium** | Resource leak (unclosed response) | `download_file` |