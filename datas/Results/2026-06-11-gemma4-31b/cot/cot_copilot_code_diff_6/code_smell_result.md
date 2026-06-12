Here is the professional code review for `bad_requests.py` based on the provided global rules and requirements.

---

### Code Review Summary
The provided code exhibits several critical software engineering anti-patterns, including poor naming conventions, lack of modularity, dangerous error handling, and reliance on global state. The function violates the Single Responsibility Principle (SRP) by mixing different API operations (GET, POST) and logging into a single block.

---

### Detailed Findings

#### 1. Code Smell Type: Violation of Single Responsibility Principle (SRP) / Long Function
- **Problem Location**: `functionThatDoesTooMuchAndIsHardToUnderstand()`
- **Detailed Explanation**: The function is attempting to perform three distinct tasks: fetching a single post, fetching all posts, and creating a new post. Mixing these concerns makes the code hard to test, reuse, or maintain. If the logic for one request changes, the entire function must be modified.
- **Improvement Suggestions**: Break the function into smaller, specialized functions (e.g., `get_post(id)`, `get_all_posts()`, and `create_post(data)`).
- **Priority Level**: High

#### 2. Code Smell Type: Unclear/Non-Standard Naming
- **Problem Location**: `functionThatDoesTooMuchAndIsHardToUnderstand`, `weirdVariableName`, `r2`
- **Detailed Explanation**: 
    - `functionThatDoesTooMuch...` is not descriptive of the business logic.
    - `weirdVariableName` provides no semantic meaning.
    - `r2` is a generic abbreviation.
    - The function name uses `camelCase`, which violates PEP 8 (Python's standard naming convention which mandates `snake_case` for functions).
- **Improvement Suggestions**: Use descriptive `snake_case` names: `fetch_single_post`, `fetch_all_posts`, `create_new_post`, and `response`.
- **Priority Level**: Medium

#### 3. Code Smell Type: Dangerous Error Handling (Bare Except / Generic Catch)
- **Problem Location**: `except Exception as e:` and `except:`
- **Detailed Explanation**: 
    - Using `except Exception` is too broad and can hide unexpected bugs (like `KeyboardInterrupt` or `MemoryError`). 
    - Using a bare `except:` is strongly discouraged in Python as it catches everything and makes debugging nearly impossible.
    - The error messages ("錯誤但我不管") are unprofessional and provide no actionable diagnostic information.
- **Improvement Suggestions**: Catch specific exceptions from the `requests` library (e.g., `requests.exceptions.RequestException`, `requests.exceptions.HTTPError`). Implement a proper logging system instead of `print`.
- **Priority Level**: High

#### 4. Code Smell Type: Misuse of Global State
- **Problem Location**: `GLOBAL_SESSION`, `ANOTHER_GLOBAL`, and `global GLOBAL_SESSION`
- **Detailed Explanation**: 
    - Relying on global variables creates tight coupling and makes unit testing difficult because the state persists between tests.
    - The `global GLOBAL_SESSION` statement inside the function is unnecessary here (as the object is mutated, not reassigned), but signals a poor architecture.
- **Improvement Suggestions**: Pass the `session` object as an argument to functions (Dependency Injection) or wrap the logic in a Class (e.g., `APIClient`).
- **Priority Level**: Medium

#### 5. Code Smell Type: Magic Strings / Hardcoded URLs
- **Problem Location**: `url = "https://jsonplaceholder.typicode.com/posts/1"` and the POST request URL.
- **Detailed Explanation**: The base URL is repeated across multiple calls. If the API endpoint changes, the developer must find and replace every instance, increasing the risk of inconsistency and bugs.
- **Improvement Suggestions**: Define a `BASE_URL` constant and use f-strings or `urljoin` to build specific endpoints.
- **Priority Level**: Low

#### 6. Code Smell Type: Lack of Resource Management & Validation
- **Problem Location**: `response = GLOBAL_SESSION.get(url)`
- **Detailed Explanation**: The code prints the status code but does not handle non-200 responses for the first and third requests. It continues execution even if the server returns a 404 or 500 error, which could lead to crashes when accessing `response.text` if the body is empty or invalid.
- **Improvement Suggestions**: Use `response.raise_for_status()` immediately after a request to ensure the program handles HTTP errors explicitly.
- **Priority Level**: High

---

### Final Recommendations Table

| Issue | Priority | Fix |
| :--- | :--- | :--- |
| **Architecture** | High | Refactor into a class or multiple small functions. |
| **Error Handling** | High | Replace `except:` with specific `requests` exceptions. |
| **Naming** | Medium | Rename to `snake_case` and use descriptive nouns. |
| **Global State** | Medium | Inject session dependencies into functions. |
| **Consistency** | Low | Centralize the Base URL into a single constant. |