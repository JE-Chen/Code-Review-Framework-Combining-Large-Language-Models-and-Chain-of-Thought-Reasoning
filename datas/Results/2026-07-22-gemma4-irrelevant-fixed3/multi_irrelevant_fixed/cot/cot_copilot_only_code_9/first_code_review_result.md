### Code Review

**Software Engineering Standards**
* **Duplicate Code:** The functions `get_users`, `get_posts`, and `get_comments` share identical logic. Refactor these into a single generic `fetch_data(endpoint)` function to improve maintainability.
* **Global State:** The use of `GLOBAL_RESULTS` creates a side-effect-driven architecture. `process_data` should return a list, and `main` should handle the output.

**Naming Conventions**
* **Vague Variable Names:** In `process_data`, the loop variables `u`, `p`, and `c` are too cryptic. Use `user`, `post`, and `comment` for better clarity.

**Logic & Correctness**
* **Missing Error Handling:** `response.json()` is called without checking `response.status_code` or calling `response.raise_for_status()`. This will lead to crashes or incorrect data if the API returns a 4xx or 5xx error.
* **Potential KeyError:** In the `posts` and `comments` loops, the code uses `.get()` for the `if` condition but direct bracket access (e.g., `p["title"]`) for the append. If the key is missing, the program will raise a `KeyError`.

**Readability & Consistency**
* **Nested Conditionals:** The result count logic in `main()` is deeply nested. Use `elif` statements to flatten the structure and improve readability.

**Performance & Security**
* **Synchronous Requests:** The code makes three sequential network calls. While acceptable for this scale, these could be performed concurrently to reduce total execution time.