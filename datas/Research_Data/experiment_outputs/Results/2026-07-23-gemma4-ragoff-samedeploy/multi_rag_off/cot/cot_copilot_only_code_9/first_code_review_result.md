### Code Review

**1. Readability & Consistency**
* **Nested Conditionals:** The `main()` function contains deeply nested `if/else` blocks for result counting. These should be flattened using `elif` for better readability.

**2. Naming Conventions**
* **Vague Variable Names:** In `process_data()`, the loop variables `u`, `p`, and `c` are too cryptic. Use `user`, `post`, and `comment` instead.
* **Vague Result Variable:** In `main()`, the variable `r` should be renamed to `result`.

**3. Software Engineering Standards**
* **Code Duplication:** The functions `get_users`, `get_posts`, and `get_comments` share identical logic. These should be refactored into a single generic function (e.g., `fetch_data(endpoint)`) to improve maintainability.
* **Global State:** The use of `GLOBAL_RESULTS` as a global list makes the code harder to test and reuse. `process_data()` should return a list, which is then passed to `main()`.

**4. Logic & Correctness**
* **Inconsistent Key Access:** In `process_data()`, the code uses `.get()` to safely check for keys but then accesses them via square brackets (e.g., `p["title"]` and `c["email"]`). If the key is missing, this will trigger a `KeyError`. Use `.get()` consistently.
* **HTTP Error Handling:** `requests.get()` does not raise an exception for 4xx or 5xx responses. Add `response.raise_for_status()` before calling `.json()` to ensure API errors are caught by the `try-except` block.

**5. Performance & Security**
* **Resource Management:** The code makes three sequential network requests. While acceptable for this scale, these could be performed concurrently if the dataset grows.

**6. Documentation & Testing**
* **Missing Documentation:** There are no docstrings explaining the purpose of the functions or the expected structure of the API responses.