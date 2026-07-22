### 1. Overall Conclusion
The PR does **not** meet merge criteria. While the code is functional for a basic scenario, it contains several critical logic flaws (potential crashes), architectural anti-patterns (global state and duplication), and robustness issues (poor error handling). These are blocking concerns that must be addressed to ensure stability and maintainability.

### 2. Comprehensive Evaluation
*   **Code Quality and Correctness:**
    *   **Critical Bugs:** There is a high risk of `KeyError` crashes in `process_data()`. The code uses `.get()` to validate the existence of keys (`title`, `email`) but then accesses those same keys using direct bracket notation (`p["title"]`, `c["email"]`), which will fail if the key is missing.
    *   **Fragile Error Handling:** The code lacks HTTP status validation. Since `requests.get()` does not raise exceptions for 4xx/5xx errors, the program may attempt to call `.json()` on invalid responses, leading to crashes. Furthermore, catching the generic `Exception` class masks potential programming errors.
*   **Maintainability and Design:**
    *   **High Duplication:** The `get_users`, `get_posts`, and `get_comments` functions are nearly identical, violating the DRY principle and increasing the maintenance burden.
    *   **Poor State Management:** The use of `GLOBAL_RESULTS` creates tight coupling and side effects, making the code difficult to test and reuse.
    *   **Readability:** The `main()` function suffers from the "Arrow Anti-pattern" due to deeply nested `if/else` blocks. Variable names in `process_data` (`u`, `p`, `c`) are non-descriptive.
*   **Consistency:**
    *   The code follows standard Python indentation and formatting, but is inconsistent in its approach to dictionary access (mixing `.get()` with direct access).

### 3. Final Decision Recommendation
**Request Changes**

**Justification:**
The PR introduces critical stability risks (`KeyError` and unhandled HTTP errors) and significant technical debt (global state and code duplication). These issues must be resolved before the code is suitable for a production environment.

### 4. Team Follow-up
*   **Refactor Data Fetching:** Consolidate the three `get_*` functions into a single `fetch_data(endpoint)` helper.
*   **Fix Logic Errors:** Replace direct dictionary access with consistent `.get()` usage or verify keys before access.
*   **Improve Robustness:** Add `response.raise_for_status()` and replace generic `Exception` catches with `requests.exceptions.RequestException`.
*   **Decouple State:** Remove `GLOBAL_RESULTS` and modify `process_data()` to return a list.
*   **Clean up Readability:** Flatten the nested logic in `main()` using `elif` and rename loop variables to `user`, `post`, and `comment`.