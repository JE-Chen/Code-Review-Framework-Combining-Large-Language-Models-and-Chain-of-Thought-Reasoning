### Code Review

#### 1. Readability & Consistency
- **Formatting:** The code is generally well-formatted and follows standard Python indentation.
- **Consistency:** The structure of the `get_*` functions is consistent, though repetitive.

#### 2. Naming Conventions
- **Variable Names:** In `process_data`, the loop variables `u`, `p`, and `c` are too concise. They should be renamed to `user`, `post`, and `comment` for better semantic clarity.

#### 3. Software Engineering Standards
- **Modularity & Duplication:** There is significant duplication across `get_users`, `get_posts`, and `get_comments`. These should be refactored into a single generic `fetch_data(endpoint)` function to improve maintainability.
- **State Management:** The use of `GLOBAL_RESULTS` as a global list is a poor practice. It makes the code harder to test and can lead to side effects if `process_data` is called multiple times. The function should return a list instead.

#### 4. Logic & Correctness
- **Exception Handling:** The `try-except` blocks catch all exceptions (`Exception`), which is too broad. It should specifically target `requests.exceptions.RequestException`.
- **HTTP Status Validation:** The code calls `.json()` immediately after the request. If the server returns a 4xx or 5xx error, `requests.get` does not raise an exception by default, and `.json()` might fail or return unexpected data. `response.raise_for_status()` should be called first.
- **Potential Crash:** In `process_data`, the code uses `p["title"]` and `c["email"]` after checking for their existence using `.get()`. If the key is missing, the `.get()` check passes (returning an empty string), but the subsequent direct access `p["title"]` will raise a `KeyError`.

#### 5. Performance & Security
- **Performance:** The data is fetched sequentially. While acceptable for this scale, these are independent I/O bound tasks that could be performed concurrently.
- **Security:** The `BASE_URL` is hardcoded. For production environments, this should be moved to an environment variable or configuration file.

#### 6. Documentation & Testing
- **Documentation:** There are no docstrings explaining the purpose of the functions or the expected structure of the API responses.
- **Testing:** No unit tests are provided to verify the filtering logic in `process_data`.

---

### Summary of Recommendations

| Category | Issue | Recommendation |
| :--- | :--- | :--- |
| **Architecture** | Code Duplication | Create a generic `fetch_data` helper function. |
| **Architecture** | Global State | Remove `GLOBAL_RESULTS`; return values from functions. |
| **Correctness** | Unsafe Dict Access | Use `.get()` consistently or verify key existence before direct access. |
| **Correctness** | HTTP Validation | Add `response.raise_for_status()` to handle API errors. |
| **Readability** | Poor Naming | Rename `u`, `p`, `c` to `user`, `post`, `comment`. |
| **Robustness** | Broad Exception | Catch `requests.RequestException` instead of `Exception`. |