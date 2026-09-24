### Code Review

**1. Logic & Correctness**
*   **Mutable Default Argument:** In `fetch_resource(url, headers={}, ...)`, the `headers` dictionary is shared across all calls to the function. Modifying it (e.g., `headers["User-Agent"] = ...`) persists those changes for subsequent calls, leading to unpredictable behavior. Use `headers=None` and initialize inside the function.
*   **Inefficient File Writing:** In `download_file`, the code accumulates the entire file into a bytes object (`content += chunk`) before writing to disk. This defeats the purpose of `stream=True` and will cause memory exhaustion for large files. Write chunks directly to the file.
*   **Shadowing Built-ins:** The function `hash(text)` shadows the Python built-in `hash()` function. Rename it to `calculate_hash` or `get_md5`.

**2. Software Engineering Standards**
*   **State Management:** Using a function attribute (`fetch_resource.cache`) as a makeshift singleton/global cache is non-standard and makes the code harder to test. Consider using a class or a dedicated cache object.
*   **Hardcoded Values:** The `chunk_size=1234` in `download_file` is an arbitrary magic number. Use a standard power-of-two value (e.g., `8192`).

**3. Readability & Naming**
*   **Variable Naming:** In `batch_fetch`, the variable `u` should be renamed to `url` for clarity.
*   **String Formatting:** In `print_summary`, the string concatenation using `+` is brittle and hard to read. Use f-strings for better readability.

**4. Performance & Security**
*   **MD5 Usage:** `hashlib.md5()` is used for checksums. While acceptable for basic integrity checks, be aware it is cryptographically broken; if security is required, use `sha256`.

### Summary of Suggested Improvements
*   Change `headers={}` to `headers=None`.
*   Write `chunk` directly to the file in `download_file` instead of appending to a variable.
*   Rename `hash()` to `calculate_md5()`.
*   Replace string concatenation in `print_summary` with f-strings.