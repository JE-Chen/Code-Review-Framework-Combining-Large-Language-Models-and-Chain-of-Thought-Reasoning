# Code Review: `bad_requests.py`

## 1. Readability & Consistency
*   **Naming Style**: The function `functionThatDoesTooMuchAndIsHardToUnderstand` uses `camelCase`, which violates PEP 8 standards for Python (should use `snake_case`).
*   **Hardcoded Values**: URLs are mixed between global constants and hardcoded strings inside the function, reducing consistency.

## 2. Naming Conventions
*   **Non-Descriptive Names**: 
    *   `functionThatDoesTooMuchAndIsHardToUnderstand`: The name describes the problem rather than the purpose of the function.
    *   `r2`: Too generic; should describe what the response represents.
    *   `weirdVariableName`: Cryptic and non-semantic.
    *   `ANOTHER_GLOBAL`: Does not describe the content (e.g., `POSTS_API_URL`).

## 3. Software Engineering Standards
*   **Lack of Modularity**: The function violates the Single Responsibility Principle. It performs three distinct network operations (GET single post, GET all posts, POST new post) in one block.
*   **Global State**: Unnecessary use of the `global` keyword inside the function for `GLOBAL_SESSION`.

## 4. Logic & Correctness
*   **Bare Except Clause**: The second `try...except:` block catches all exceptions without specifying a type, which can hide critical bugs (e.g., `KeyboardInterrupt`).
*   **Poor Error Handling**: Using `print("錯誤但我不管")` is insufficient for production; errors should be logged or raised appropriately.

## 5. Performance & Security
*   **Input Validation**: No timeout specified in `requests.get()` or `requests.post()`, which could lead to the program hanging indefinitely if the server does not respond.

---

## Summary of Suggestions
*   **Refactor** the large function into three smaller, focused functions (e.g., `get_post`, `list_posts`, `create_post`).
*   **Rename** variables and functions to follow `snake_case` and descriptive naming (e.g., `response_all_posts` instead of `r2`).
*   **Improve Exception Handling** by catching specific errors (e.g., `requests.exceptions.RequestException`) and avoiding bare `except` blocks.
*   **Add Timeouts** to all network requests to prevent hanging.