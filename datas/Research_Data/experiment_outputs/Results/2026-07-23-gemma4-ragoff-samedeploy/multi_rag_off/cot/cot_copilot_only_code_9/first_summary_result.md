### Code Review

#### 1. Readability & Consistency
- **Formatting:** The code is generally well-formatted and follows standard Python indentation.
- **Consistency:** The structure of the `get_*` functions is consistent, though repetitive.

#### 2. Naming Conventions
- **Variable Names:** `u`, `p`, and `c` in the `process_data` loops are too concise. They should be renamed to `user`, `post`, and `comment` for better semantic clarity.
- **Global Variable:** `GLOBAL_RESULTS` follows the constant naming convention (UPPER_CASE), but it is being used as a mutable global state, which is generally discouraged.

#### 3. Software Engineering Standards
- **Modularity & Duplication:** There is significant duplication in `get_users`, `get_posts`, and `get_comments`. These should be refactored into a single generic `fetch_data(endpoint)` function to improve maintainability.
- **State Management:** The use of a global list (`GLOBAL_RESULTS`) makes the code harder to test and reuse. `process_data` should return a list, which is then passed to `main`.

#### 4. Logic & Correctness
- **Exception Handling:** The `try-except` blocks catch all exceptions (`Exception`), which is too broad. It should specifically target `requests.exceptions.RequestException`.
- **HTTP Status Validation:** The code calls `.json()` immediately after the request. If the server returns a 4xx or 5xx error, `requests.get` does not raise an exception by default, but the response body might not be valid JSON or might represent an error. `response.raise_for_status()` should be called before `.json()`.
- **Potential KeyError:** In `process_data`, the code uses `.get()` for the `if` condition but uses direct key access `p["title"]` and `c["email"]` for the append operation. If the key is missing, the program will crash with a `KeyError`.

#### 5. Performance & Security
- **Performance:** The three API calls are performed sequentially. While acceptable for this scale, they could be performed concurrently using `asyncio` or `concurrent.futures` if the dataset grows.
- **Security:** The `BASE_URL` is hardcoded. For production environments, this should be moved to an environment variable or configuration file.

#### 6. Documentation & Testing
- **Documentation:** The code lacks docstrings for functions and a module-level description.
- **Testing:** No unit tests are provided. The logic in `process_data` (filtering by ID 5, title length > 20, and email presence) is highly specific and requires automated tests to ensure correctness.

---

### Summary of Recommendations

| Category | Issue | Recommendation |
| :--- | :--- | :--- |
| **Engineering** | Code Duplication | Create a generic `fetch_data(endpoint)` function. |
| **Engineering** | Global State | Remove `GLOBAL_RESULTS`; return values from functions. |
| **Logic** | Error Handling | Use `response.raise_for_status()` and catch specific `requests` exceptions. |
| **Logic** | Potential Crash | Use `.get()` consistently or verify key existence before direct access. |
| **Naming** | Non-descriptive names | Rename `u`, `p`, `c` to `user`, `post`, `comment`. |
| **Docs** | Missing Documentation | Add docstrings to all functions. |