### Code Review

**1. Logic & Correctness**
*   **Mutable Default Argument:** In `fetch_resource(url, headers={})`, the `headers` dictionary is shared across all calls. Modifying it (e.g., `headers["User-Agent"] = ...`) persists changes to subsequent calls, leading to unpredictable behavior. Use `headers=None` and initialize inside the function.
*   **Shadowing Built-ins:** The function `hash(text)` shadows the Python built-in `hash()` function. Rename it to `calculate_hash` or `get_md5_hash`.
*   **Resource Leak:** In `download_file`, the `requests.get(url, stream=True)` response is not closed. Use a `with` statement to ensure the connection is released.
*   **Inefficient String Concatenation:** In `download_file`, `content += chunk` creates a new bytes object in every iteration. Use a list and `b"".join(chunks)` or write chunks directly to the file.

**2. Naming Conventions**
*   **Vague Variable Names:** `r` (used in multiple functions) should be renamed to `response` for better clarity.
*   **Non-Descriptive Names:** `u` in `batch_fetch` should be `url`.

**3. Software Engineering Standards**
*   **State Management:** Using a function attribute (`fetch_resource.cache`) as a makeshift singleton is unconventional and hard to test. Consider using a class or a dedicated cache object.
*   **Hardcoded Values:** The `chunk_size=1234` in `download_file` is an arbitrary magic number; it should be a named constant or a parameter.

**4. Performance & Security**
*   **MD5 Usage:** `hashlib.md5` is cryptographically broken. While acceptable for simple checksums, it should be noted if this is intended for security purposes.

**5. Readability & Consistency**
*   **String Formatting:** `print_summary` uses manual string concatenation (`+`). Use f-strings for better readability and performance.

### Summary of Suggested Improvements
*   Change `headers={}` to `headers=None`.
*   Rename `hash()` to `calculate_md5()`.
*   Wrap `requests.get(stream=True)` in a `with` block.
*   Replace `content += chunk` with direct file writes: `f.write(chunk)`.
*   Use f-strings in `print_summary`.