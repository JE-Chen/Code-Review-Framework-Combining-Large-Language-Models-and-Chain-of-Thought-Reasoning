### Pull Request Summary

*   **Key changes**: Implemented a data retrieval and processing pipeline that fetches users, posts, and comments from a REST API and filters them based on specific criteria.
*   **Impact scope**: New script introducing API integration and basic data filtering logic.
*   **Purpose of changes**: Feature addition to aggregate specific data points from the JSONPlaceholder API.
*   **Items to confirm**: Review the error handling strategy and the use of global state for result accumulation.

---

### Code Review

#### 1. Readability & Consistency
*   **Formatting**: The code is generally well-formatted and follows PEP 8 indentation.
*   **Consistency**: The structure of the `get_*` functions is consistent.

#### 2. Naming Conventions
*   **Variable Names**: In `process_data`, the loop variables `u`, `p`, and `c` are too concise. They should be renamed to `user`, `post`, and `comment` to maintain semantic clarity.

#### 3. Software Engineering Standards
*   **Modularization/DRY**: There is significant duplication in `get_users`, `get_posts`, and `get_comments`. These should be refactored into a single generic `fetch_data(endpoint)` function to reduce redundancy.
*   **Global State**: The use of `GLOBAL_RESULTS` is a bad practice. It makes the code harder to test and not thread-safe. `process_data` should return a list, which is then passed to `main`.

#### 4. Logic & Correctness
*   **Exception Handling**: The `try-except` blocks catch `Exception`, which is too broad. It should specifically catch `requests.exceptions.RequestException`.
*   **HTTP Status Validation**: The code calls `.json()` immediately after the request. If the server returns a 404 or 500 error, `requests.get` does not raise an exception, but the response body might not be valid JSON or might contain an error message. Use `response.raise_for_status()` before parsing.
*   **Potential Crash**: In `process_data`, the code uses `p["title"]` and `c["email"]` after checking for their existence using `.get()`. If the key is missing, the `.get()` check passes (returning an empty string), but the subsequent direct access `p["title"]` will raise a `KeyError`. Use the variable captured from `.get()` or ensure the key exists.

#### 5. Performance & Security
*   **Performance**: The requests are made sequentially. For a larger number of endpoints, using `asyncio` or a `ThreadPoolExecutor` would improve performance.
*   **Security**: The `BASE_URL` is hardcoded. While acceptable for a script, it should ideally be moved to an environment variable or configuration file for better flexibility.

#### 6. Documentation & Testing
*   **Documentation**: The code lacks docstrings for functions.
*   **Testing**: No unit tests are provided. The logic in `process_data` (filtering) is currently coupled with the API calls, making it impossible to test without making network requests.

### Summary of Suggested Refactoring
1.  Create a `fetch_resource(endpoint)` helper.
2.  Change `process_data` to return a list instead of modifying a global variable.
3.  Replace `u`, `p`, `c` with descriptive names.
4.  Add `response.raise_for_status()` to handle HTTP errors.
5.  Fix the `KeyError` risk in the filtering loops.