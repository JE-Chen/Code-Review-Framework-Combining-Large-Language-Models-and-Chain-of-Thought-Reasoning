### 1. Overall Conclusion
The PR does **not** meet the merge criteria. While the code successfully implements the basic requirement of fetching and filtering data, it contains several **blocking concerns** regarding stability (potential crashes), maintainability (significant code duplication), and software engineering best practices (global state mutation).

### 2. Comprehensive Evaluation
*   **Code Quality and Correctness**:
    *   **Critical Bug**: There is a high risk of `KeyError` crashes in `process_data`. The code uses `.get()` to validate the existence of keys (e.g., `p.get("title")`) but then accesses those same keys using bracket notation (e.g., `p["title"]`). If a key is missing, the check may pass (returning an empty string), but the subsequent access will crash the program.
    *   **Fragile Error Handling**: The use of a broad `except Exception` block hides specific failure modes and may catch system-level interrupts. Additionally, the code lacks `response.raise_for_status()`, meaning it will attempt to parse `.json()` even if the server returns a 4xx or 5xx error.
*   **Maintainability and Design**:
    *   **DRY Violation**: `get_users`, `get_posts`, and `get_comments` are nearly identical. This duplication increases the effort required for any future changes to the request logic.
    *   **Architectural Flaw**: The use of `GLOBAL_RESULTS` creates tight coupling between `process_data` and `main`, hindering testability and preventing the code from being thread-safe.
    *   **Readability**: Loop variables (`u`, `p`, `c`) are non-descriptive, and the result-reporting logic in `main()` suffers from the "Arrow Anti-pattern" due to deeply nested `if/else` blocks.
*   **Consistency**:
    *   The code follows PEP 8 indentation and maintains a consistent structure across the duplicated functions.

### 3. Final Decision Recommendation
**Request Changes**

**Justification**:
The PR requires refactoring to resolve a potential runtime crash (`KeyError`), the removal of global state to ensure the code is testable, and the consolidation of duplicated API logic to meet basic software engineering standards.

### 4. Team Follow-up
*   **Refactor API Logic**: Replace the three `get_*` functions with a single `fetch_data(endpoint)` helper.
*   **Fix State Management**: Modify `process_data()` to return a list of results instead of mutating `GLOBAL_RESULTS`.
*   **Stabilize Data Access**: Ensure consistent use of `.get()` or variable assignment when accessing dictionary keys to prevent `KeyError`.
*   **Improve Error Handling**: Implement `response.raise_for_status()` and catch `requests.exceptions.RequestException` specifically.
*   **Clean up Logic**: Flatten the nested conditionals in `main()` using `elif` statements and rename loop variables to `user`, `post`, and `comment`.