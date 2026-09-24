Here is the code review based on the provided global rules.

### 1. Readability & Consistency
*   **Formatting:** The code is generally well-formatted and follows standard Python indentation.
*   **Consistency:** The structure of the `get_*` functions is consistent, though repetitive.

### 2. Naming Conventions
*   **Variable Names:** In `process_data`, the loop variables `u`, `p`, and `c` are too concise. They should be renamed to `user`, `post`, and `comment` to maintain semantic clarity.
*   **Global Variable:** `GLOBAL_RESULTS` follows the constant naming convention (UPPER_CASE), but since it is being mutated as a list, it acts as a global state variable rather than a constant.

### 3. Software Engineering Standards
*   **Modularity & DRY (Don't Repeat Yourself):** There is significant duplication in `get_users`, `get_posts`, and `get_comments`. These should be refactored into a single generic function (e.g., `fetch_data(endpoint)`).
*   **State Management:** The use of a global list (`GLOBAL_RESULTS`) makes the code harder to test and maintain. `process_data` should return a list, which is then passed to `main`.

### 4. Logic & Correctness
*   **Exception Handling:** The `try-except` blocks catch the generic `Exception`. This is too broad. It should specifically catch `requests.exceptions.RequestException`.
*   **HTTP Status Validation:** The code calls `.json()` immediately after the request. If the server returns a 404 or 500 error, `requests.get` does not raise an exception, but the response body might not be valid JSON, leading to a crash. `response.raise_for_status()` should be called before `.json()`.
*   **Potential KeyError:** In the `posts` and `comments` loops, the code uses `.get()` for the `if` condition but uses direct bracket access `p["title"]` and `c["email"]` for the append. If the key is missing, the program will crash with a `KeyError`.

### 5. Performance & Security
*   **Performance:** The requests are made sequentially. While acceptable for this scale, using a `requests.Session()` would improve performance by reusing TCP connections.
*   **Security:** The `BASE_URL` is hardcoded. For production-ready code, this should be moved to an environment variable or configuration file.

### 6. Documentation & Testing
*   **Documentation:** There are no docstrings for the functions. The purpose of `process_data` (which seems to be a specific filter/aggregation) is not documented.
*   **Testing:** No unit tests are provided. The logic in `process_data` is currently tightly coupled to the network calls, making it difficult to test without mocking.

---

### Summary of Recommendations

| Category | Issue | Recommendation |
| :--- | :--- | :--- |
| **Engineering** | Code Duplication | Create a helper function `fetch_resource(endpoint)`. |
| **Logic** | Unsafe JSON parsing | Add `response.raise_for_status()` before calling `.json()`. |
| **Logic** | Potential `KeyError` | Use `.get()` consistently or verify key existence before bracket access. |
| **Engineering** | Global State | Remove `GLOBAL_RESULTS` and return values from functions. |
| **Readability** | Poor naming | Rename `u`, `p`, `c` to `user`, `post`, `comment`. |
| **Correctness** | Broad Exception | Catch `requests.RequestException` instead of `Exception`. |