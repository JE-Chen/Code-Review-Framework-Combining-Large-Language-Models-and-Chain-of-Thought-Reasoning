Here is the code review for `bad_requests.py` based on the provided global rules.

### 1. Readability & Consistency
*   **Formatting:** The code generally follows basic indentation, but the `POST` request call is split across lines in a way that is slightly inconsistent with standard PEP 8 spacing.
*   **Language Consistency:** The `print` statements mix English and Traditional Chinese (e.g., `"狀態碼:"` vs `"POST 結果:"`). For professional codebases, it is recommended to stick to one language (usually English) for logs and console output.

### 2. Naming Conventions
*   **Function Naming:** `functionThatDoesTooMuchAndIsHardToUnderstand` violates standard Python naming conventions (should be `snake_case`) and is not descriptive of the actual business logic.
*   **Variable Naming:** `r2` and `weirdVariableName` are non-descriptive. Variables should reflect the data they hold (e.g., `posts_response` or `create_post_response`).

### 3. Software Engineering Standards
*   **Modularity:** The function violates the **Single Responsibility Principle**. It performs three distinct actions: fetching a single post, fetching all posts, and creating a post. These should be split into three separate functions.
*   **Hardcoded Values:** URLs are hardcoded inside the function. These should be moved to constants or a configuration file to improve maintainability.

### 4. Logic & Correctness
*   **Exception Handling:** 
    *   The first `try-except` block catches `Exception`, which is too broad.
    *   The second `try-except` block is a **bare except** (`except:`), which is a dangerous practice in Python as it catches `SystemExit` and `KeyboardInterrupt`, making it difficult to stop the program.
*   **Error Silencing:** The print statements `"錯誤但我不管"` (Error but I don't care) indicate that errors are being swallowed without proper logging or recovery logic, which will make debugging in production impossible.
*   **Response Validation:** The first request does not check if the response was successful (e.g., `response.raise_for_status()`) before printing the text.

### 5. Performance & Security
*   **Global State:** The use of `global GLOBAL_SESSION` inside the function is unnecessary because `GLOBAL_SESSION` is being accessed/read, not reassigned. Even so, relying on global sessions can lead to issues in multi-threaded environments.
*   **Resource Management:** While `requests.Session()` is used (which is good for performance), there is no mechanism to close the session when the application terminates.

### 6. Documentation & Testing
*   **Documentation:** There are no docstrings or comments explaining the purpose of the script or the expected behavior of the functions.
*   **Testing:** No unit tests are provided to verify the API interactions or the error handling logic.

---

### Summary of Recommendations
| Category | Issue | Priority | Recommendation |
| :--- | :--- | :--- | :--- |
| **Naming** | Non-standard/Non-descriptive names | High | Rename to `snake_case` and use meaningful names. |
| **Logic** | Bare `except:` block | High | Replace with specific exceptions (e.g., `requests.RequestException`). |
| **Architecture** | Monolithic function | Medium | Refactor into smaller, single-purpose functions. |
| **Consistency** | Mixed language in prints | Low | Standardize output language to English. |