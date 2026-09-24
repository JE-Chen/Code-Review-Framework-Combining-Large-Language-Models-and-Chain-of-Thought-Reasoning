### Code Review

#### 1. Logic & Correctness
*   **Mutable Default Argument:** In `fetch_resource`, `headers={}` is a mutable default argument. This causes the `headers` dictionary to be shared across all calls to the function, leading to unexpected state leakage.
*   **Input Mutation:** `fetch_resource` modifies the `headers` dictionary directly (`headers["User-Agent"] = ...`). This mutates the caller's object, which can cause side effects in `batch_fetch`.
*   **Shadowing Built-ins:** The function `hash(text)` shadows the Python built-in `hash()` function, which can lead to confusion and bugs.

#### 2. Software Engineering Standards
*   **Shared Mutable State:** `fetch_resource` uses a function attribute (`fetch_resource.cache`) as a global cache. This makes the function harder to test and reason about. Consider using a class or an explicit cache object.
*   **Single Responsibility:** `download_file` handles both the network request and the file system I/O. These should be separated to improve testability.
*   **Magic Numbers:** The `chunk_size=1234` and `len(content) > 3000` in `download_file` are magic numbers. These should be defined as named constants.

#### 3. Performance & Security
*   **Inefficient String Concatenation:** In `download_file`, `content += chunk` creates a new bytes object in every iteration. For large files, this results in quadratic time complexity. Use a list and `b"".join()` or write chunks directly to the file.
*   **Resource Management:** `download_file` reads the entire content into memory before writing to disk. For large files, this can cause an `OutOfMemory` error. Write chunks to the file inside the loop.
*   **MD5 Usage:** `hashlib.md5()` is used for checksums. While acceptable for non-security integrity checks, ensure it is not used for security-sensitive hashing.

#### 4. Readability & Naming
*   **Vague Naming:** Variable names like `r`, `u`, `h`, and `f` are too short. Use descriptive names like `response`, `url`, `hasher`, and `file`.
*   **String Formatting:** `print_summary` uses manual string concatenation (`+`). Use f-strings for better readability and performance.

#### 5. Documentation & Testing
*   **Missing Error Handling:** There are no `try-except` blocks around `requests.get` or `open()`. Network timeouts or permission errors will crash the program.
*   **Lack of Type Hints:** Adding type hints to function signatures would improve clarity and maintainability.