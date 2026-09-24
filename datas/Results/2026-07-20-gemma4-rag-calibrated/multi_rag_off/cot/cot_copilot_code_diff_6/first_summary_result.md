Here is the code review for `bad_requests.py` based on the provided global rules.

### 1. Readability & Consistency
- **Formatting:** The code lacks consistent spacing around operators and follows a mix of styles.
- **Language Consistency:** The `print` statements use a mix of English and Traditional Chinese (e.g., `"狀態碼:"` vs `"POST 結果:"`). For professional codebases, it is recommended to stick to one language (usually English) for logs and output.

### 2. Naming Conventions
- **Function Naming:** `functionThatDoesTooMuchAndIsHardToUnderstand` violates standard Python naming conventions (PEP 8). It should use `snake_case` (e.g., `fetch_and_post_data`). Furthermore, the name is self-deprecating rather than descriptive of the function's actual purpose.
- **Variable Naming:** `r2` and `weirdVariableName` are not descriptive. `r2` should be `response` or `posts_response`, and `weirdVariableName` should be `post_response`.

### 3. Software Engineering Standards
- **Modularity:** The function violates the Single Responsibility Principle. It performs three distinct actions: fetching a single post, fetching all posts, and creating a post. These should be split into three separate functions.
- **Hardcoded Values:** URLs are hardcoded inside the function. These should be moved to constants or configuration files to improve maintainability.

### 4. Logic & Correctness
- **Exception Handling:** 
    - The use of `except Exception as e:` and a bare `except:` is poor practice. It catches all errors (including `KeyboardInterrupt`), making debugging difficult.
    - The error handling only prints the error and continues execution, which may lead to crashes later if the code depends on the failed request's output.
- **Global State:** The use of `global GLOBAL_SESSION` inside the function is unnecessary because the session is being accessed, not reassigned.

### 5. Performance & Security
- **Resource Management:** While a `requests.Session()` is used (which is good for performance), there is no timeout specified in the `.get()` or `.post()` calls. This can lead to the application hanging indefinitely if the server does not respond.

### 6. Documentation & Testing
- **Documentation:** There are no docstrings or comments explaining the purpose of the script or the expected behavior of the functions.
- **Testing:** No unit tests are provided to verify the API interactions or error handling logic.

---

### Summary of Recommendations
| Category | Issue | Recommendation |
| :--- | :--- | :--- |
| **Naming** | Non-standard function/variable names | Rename to `snake_case` and use descriptive terms. |
| **Architecture** | Monolithic function | Split into `get_post()`, `get_all_posts()`, and `create_post()`. |
| **Error Handling** | Bare `except` blocks | Catch specific exceptions (e.g., `requests.RequestException`). |
| **Stability** | Missing timeouts | Add `timeout=...` to all network requests. |
| **Consistency** | Mixed language output | Standardize all print/log messages to English. |