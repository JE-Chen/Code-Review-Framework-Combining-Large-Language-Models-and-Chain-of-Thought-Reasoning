### Code Review

**Logic & Correctness**
*   **Mutable Default Argument:** In `fetch_resource`, `headers={}` is a mutable default argument. Changes made to `headers` (like adding the User-Agent) will persist across function calls, potentially leaking headers between different requests.
*   **Shadowing Built-in:** The function `hash(text)` shadows the Python built-in `hash()` function, which can lead to confusion and bugs.
*   **Inefficient File Writing:** In `download_file`, the code accumulates the entire file into a bytes object (`content += chunk`) before writing. This defeats the purpose of `stream=True` and will cause memory exhaustion for large files.

**Software Engineering Standards**
*   **State Management:** Using a function attribute (`fetch_resource.cache`) as a cache is unconventional and makes the code harder to test and maintain. Consider a class or a dedicated cache object.
*   **Hardcoded Values:** The `chunk_size=1234` in `download_file` is an arbitrary magic number; it should be a named constant or a parameter.

**Naming Conventions**
*   **Vague Variable Names:** Variables like `r` (response), `u` (url), and `f` (file) are too cryptic. Use descriptive names like `response`, `url`, and `file_handle`.

**Readability & Consistency**
*   **String Concatenation:** In `print_summary`, the use of `+` for building the summary line is less readable and less efficient than f-strings.

**Suggestions for Improvement**
*   Change `headers={}` to `headers=None` and initialize inside the function: `headers = headers or {}`.
*   Rename `hash()` to `calculate_checksum()` or `get_md5()`.
*   In `download_file`, write chunks directly to the file: `f.write(chunk)`.
*   Use f-strings for formatting output in `print_summary`.