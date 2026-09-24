### Code Review

**1. Software Engineering Standards (Modularity & DRY)**
*   **Duplicate Code:** The functions `get_users`, `get_posts`, and `get_comments` are nearly identical. 
    *   *Suggestion:* Create a single generic function `fetch_data(endpoint)` to handle the request and exception logic.
*   **Global State:** The use of `GLOBAL_RESULTS` creates a side-effect-driven architecture that makes the code harder to test and reuse.
    *   *Suggestion:* Have `process_data()` return a list and pass that list into `main()`.

**2. Naming Conventions**
*   **Vague Variable Names:** In `process_data`, the loop variables `u`, `p`, and `c` are too cryptic.
    *   *Suggestion:* Rename to `user`, `post`, and `comment`.

**3. Logic & Correctness**
*   **Potential Crash (KeyError):** In the `posts` and `comments` loops, you use `.get()` for the `if` condition but direct bracket access `p["title"]` and `c["email"]` for the append. If the key is missing, the program will crash.
    *   *Suggestion:* Use the value returned by `.get()` or ensure the key exists before accessing it.
*   **HTTP Error Handling:** `requests.get()` does not raise an exception for 4xx or 5xx responses. The current `try-except` only catches network-level failures.
    *   *Suggestion:* Call `response.raise_for_status()` after the request to trigger the exception block on HTTP errors.

**4. Readability & Formatting**
*   **Nested Conditionals:** The result count logic in `main()` is deeply nested.
    *   *Suggestion:* Use `if / elif / else` blocks to flatten the structure.

**5. Performance**
*   **Sequential Requests:** The three API calls are made sequentially. While acceptable for this scale, it is a bottleneck for larger datasets.
    *   *Suggestion:* Consider using `asyncio` or `concurrent.futures` if performance becomes an issue.