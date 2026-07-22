### Code Review

**1. Logic & Correctness**
*   **Mutable Default Argument:** In `fetch_resource(url, headers={}, ...)`, the `headers` dictionary is shared across all calls. Modifying it (e.g., `headers["User-Agent"] = ...`) persists changes to subsequent calls, leading to unpredictable behavior. Use `headers=None` and initialize inside the function.
*   **Resource Leak:** In `download_file`, the `requests.get(url, stream=True)` response object is not closed. Use a `with` statement to ensure the connection is released.
*   **Inefficient String Concatenation:** In `download_file`, `content += chunk` creates a new bytes object in every iteration. For large files, this causes quadratic time complexity. Use a list and `b"".join(chunks)` or write chunks directly to the file.

**2. Naming Conventions**
*   **Shadowing Built-ins:** The function `hash(text)` shadows the Python built-in `hash()` function. Rename it to `calculate_checksum` or `get_md5_hash`.
*   **Vague Variable Names:** In `batch_fetch`, the variable `u` should be renamed to `url` for clarity.

**3. Software Engineering Standards**
*   **State Management:** Using a function attribute (`fetch_resource.cache`) as a cache is unconventional and makes the code harder to test/reset. Consider using a class or a dedicated cache object/decorator (e.g., `functools.lru_cache`).
*   **Hardcoded Values:** The `chunk_size=1234` in `download_file` is an arbitrary magic number. Use a standard power-of-two size (e.g., `1024` or `8192`).

**4. Readability & Consistency**
*   **String Formatting:** In `print_summary`, the manual string concatenation (`+ " | " +`) is brittle and hard to read. Use f-strings for better readability.

**5. Performance & Security**
*   **Hashing Algorithm:** `hashlib.md5()` is used. While acceptable for simple checksums, it is cryptographically broken. If security is required, use `sha256`.