Here is the code review based on the provided global rules.

### 1. Readability & Consistency
*   **String Formatting:** In `print_summary`, the code uses string concatenation (`+`). This is less readable and less efficient than f-strings (available in Python 3.6+).
    *   *Recommendation:* Use `print(f"{r['url']} | {r['status']} | ...")`.

### 2. Naming Conventions
*   **Shadowing Built-ins:** The function `hash(text)` shadows the Python built-in `hash()` function. This can lead to confusing bugs and is against standard naming conventions.
    *   *Recommendation:* Rename to `calculate_checksum` or `get_md5_hash`.

### 3. Software Engineering Standards
*   **Mutable Default Arguments:** In `fetch_resource(url, headers={}, ...)`, the `headers` dictionary is a mutable default argument. In Python, this dictionary is shared across all calls to the function. If one call modifies `headers`, those modifications persist for subsequent calls.
    *   *Recommendation:* Use `headers=None` and initialize inside the function: `if headers is None: headers = {}`.
*   **State Management:** Using a function attribute (`fetch_resource.cache`) as a makeshift singleton/global cache is unconventional and makes the code harder to test and reset.
    *   *Recommendation:* Use a class-based approach or a dedicated cache object/decorator (e.g., `functools.lru_cache`).

### 4. Logic & Correctness
*   **Resource Leakage:** In `download_file`, `requests.get(url, stream=True)` is called, but the response object is never closed. When using `stream=True`, it is critical to ensure the connection is closed.
    *   *Recommendation:* Use a `with requests.get(...) as resp:` block.
*   **Memory Inefficiency:** In `download_file`, the code iterates through chunks but appends them all to a bytes object (`content += chunk`) before writing to a file. This defeats the purpose of `stream=True` and `chunk_size`, as the entire file is still loaded into RAM.
    *   *Recommendation:* Write chunks directly to the file inside the loop: `f.write(chunk)`.
*   **Exception Handling:** There is a total absence of `try...except` blocks. Network requests are prone to timeouts, DNS failures, and connection resets.
    *   *Recommendation:* Wrap `requests.get` calls in try-except blocks to handle `requests.exceptions.RequestException`.

### 5. Performance & Security
*   **Security (Hashing):** The code uses `MD5` for checksums. While acceptable for basic integrity checks, MD5 is cryptographically broken.
    *   *Recommendation:* If this is for security/verification, use `hashlib.sha256`.
*   **Performance:** In `batch_fetch`, requests are performed sequentially. For a large list of URLs, this will be very slow.
    *   *Recommendation:* Consider using `concurrent.futures` or `aiohttp` for parallel fetching.

### 6. Documentation & Testing
*   **Missing Documentation:** There are no docstrings for the functions. The purpose of `mode` in `batch_fetch` or the `preview` flag in `download_file` is only evident by reading the implementation.
*   **Testing:** No unit tests are provided to verify the caching logic or the checksum calculations.

---

### Summary of Major Issues
| Severity | Issue | Location |
| :--- | :--- | :--- |
| **High** | Mutable default argument (`headers={}`) | `fetch_resource` |
| **High** | Memory inefficiency (streaming to RAM) | `download_file` |
| **Medium** | Shadowing built-in `hash()` | `hash()` |
| **Medium** | Lack of error handling for network I/O | Global |
| **Low** | Use of MD5 and string concatenation | Global |