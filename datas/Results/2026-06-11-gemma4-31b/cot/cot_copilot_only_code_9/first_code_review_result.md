## Code Review Report

### 1. Readability & Consistency
*   **Nested Conditionals:** The result-counting logic in `main()` uses deeply nested `if/else` blocks. This reduces readability.
*   **String Concatenation:** The code uses `+` for string building. Using f-strings (e.g., `f"Special User: {name}"`) is more consistent with modern Python standards.

### 2. Naming Conventions
*   **Vague Variables:** Variables `u`, `p`, `c`, and `r` are too cryptic. Use `user`, `post`, `comment`, and `result` for better semantic clarity.
*   **Global Variable:** `GLOBAL_RESULTS` uses a global state, which can lead to side effects and makes the code harder to test.

### 3. Software Engineering Standards
*   **Code Duplication:** `get_users`, `get_posts`, and `get_comments` are identical in logic. These should be refactored into a single generic function (e.g., `fetch_data(endpoint)`).
*   **Modularity:** `process_data` handles both filtering logic and data modification (appending to a global list). Logic should be separated from state management.

### 4. Logic & Correctness
*   **Missing Status Checks:** `requests.get()` is called, but `response.raise_for_status()` is not used. If the server returns a 404 or 500 error, the code will try to parse the error page as JSON and potentially crash.
*   **Dict Access Inconsistency:** The code mixes `.get()` (safe) and `["key"]` (unsafe) access. For example, `p["title"]` will raise a `KeyError` if the title is missing, despite the prior check using `.get()`.

### 5. Performance & Security
*   **Synchronous Requests:** The three API calls are sequential. While acceptable for this scale, they could be performed concurrently to improve performance.
*   **Broad Exception Handling:** `except Exception as e` catches everything, including keyboard interrupts. Catch specific exceptions like `requests.RequestException`.

### 6. Documentation & Testing
*   **Missing Documentation:** There are no docstrings or type hints for the functions, making it unclear what the expected input/output types are.
*   **Lack of Tests:** No unit tests are provided for the filtering logic or API handling.

---

### Summary of Improvement Suggestions
*   **Refactor API Calls:** Create one function: `def fetch_data(endpoint):`.
*   **Remove Globals:** Pass lists as arguments and return them from functions instead of using `GLOBAL_RESULTS`.
*   **Clean up Conditionals:** Use `elif` in `main()` to flatten the nested if-statements.
*   **Improve Naming:** Rename loop variables from single letters to descriptive nouns.
*   **Add Safety:** Add `response.raise_for_status()` after every API request.