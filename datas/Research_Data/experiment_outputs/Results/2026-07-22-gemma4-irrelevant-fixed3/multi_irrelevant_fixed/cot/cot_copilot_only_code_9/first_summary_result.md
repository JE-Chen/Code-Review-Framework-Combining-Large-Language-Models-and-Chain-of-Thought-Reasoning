### Code Review

#### 1. Readability & Consistency
- **Formatting:** The code is generally well-formatted and follows standard Python indentation.
- **Consistency:** The structure of the `get_*` functions is consistent, though repetitive.

#### 2. Naming Conventions
- **Variable Names:** In `process_data`, the loop variables `u`, `p`, and `c` are too concise. They should be renamed to `user`, `post`, and `comment` for better semantic clarity.

#### 3. Software Engineering Standards
- **Modularity & Duplication:** There is significant duplication across `get_users`, `get_posts`, and `get_comments`. These should be refactored into a single generic `fetch_data(endpoint)` function to improve maintainability.
- **State Management:** The use of `GLOBAL_RESULTS` as a global list is a poor practice. It makes the code harder to test and can lead to side effects. `process_data` should return a list, which is then passed to `main`.

#### 4. Logic & Correctness
- **Exception Handling:** The `try-except` blocks catch all exceptions (`Exception`), which is too broad. It should specifically target `requests.exceptions.RequestException`.
- **HTTP Status Validation:** The code calls `.json()` immediately after the request without checking if the response was successful (e.g., `response.raise_for_status()`). If the server returns a 404 or 500, the code may crash or return unexpected data.
- **Key Access:** In `process_data`, the code uses `.get()` for the `if` condition but uses direct bracket access `p["title"]` and `c["email"]` for the append operation. If the key is missing, this will raise a `KeyError`.

#### 5. Performance & Security
- **Performance:** The three API calls are performed sequentially. While acceptable for this scale, they could be performed concurrently using `asyncio` or `concurrent.futures` if the dataset grows.

#### 6. Documentation & Testing
- **Documentation:** The code lacks docstrings for functions and a module-level description.
- **Testing:** No unit tests are provided to verify the filtering logic or the API integration.

---

### Suggested Refactoring (Summary)
1. Create a helper function `fetch_resource(endpoint)` to handle requests and error checking.
2. Remove `GLOBAL_RESULTS` and return values from functions.
3. Use descriptive loop variable names.
4. Add `response.raise_for_status()` to ensure API calls succeeded before parsing JSON.

### Score: ⚠️ Needs Improvement
The code is functional for a script but fails several software engineering standards regarding duplication, state management, and robust error handling.