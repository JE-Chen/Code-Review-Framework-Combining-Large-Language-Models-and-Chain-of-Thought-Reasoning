### Code Review

**1. Readability & Consistency**
* **Nested Conditionals:** The `main()` function contains deeply nested `if/else` blocks for result counting. These should be flattened using `elif` for better readability.

**2. Naming Conventions**
* **Vague Variable Names:** In `process_data()`, the loop variables `u`, `p`, and `c` are too cryptic. Use `user`, `post`, and `comment` instead.

**3. Software Engineering Standards**
* **Code Duplication:** `get_users`, `get_posts`, and `get_comments` share identical logic. These should be refactored into a single generic function (e.g., `fetch_data(endpoint)`) to improve maintainability.
* **Global State:** The use of `GLOBAL_RESULTS` as a global list makes the code harder to test and reuse. `process_data()` should return a list, which is then passed to `main()`.

**4. Logic & Correctness**
* **Potential KeyError:** In `process_data()`, `p["title"]` and `c["email"]` are accessed directly after using `.get()` in the `if` condition. If the key is missing, the program will crash with a `KeyError`. Use `.get()` consistently.
* **HTTP Error Handling:** `requests.get()` does not raise an exception for 4xx or 5xx responses. Add `response.raise_for_status()` to ensure errors are caught by the `try-except` block.

**5. Performance & Security**
* **Synchronous Requests:** The three API calls are made sequentially. While acceptable for this scale, they could be performed concurrently to improve performance.

**6. Documentation & Testing**
* **Missing Documentation:** The functions lack docstrings explaining their purpose and return types.