### Code Review

**Software Engineering Standards & Modularity**
* **Duplicate Code:** The functions `get_users`, `get_posts`, and `get_comments` share identical logic. Refactor these into a single generic function (e.g., `fetch_data(endpoint)`) to improve maintainability.
* **Global State:** The use of `GLOBAL_RESULTS` creates a hidden dependency and makes the code harder to test. Pass data as arguments and return results from `process_data()` instead.

**Naming Conventions**
* **Vague Naming:** In `process_data`, the loop variables `u`, `p`, and `c` are too cryptic. Use descriptive names like `user`, `post`, and `comment`.

**Logic & Correctness**
* **Potential Crash:** In the `posts` and `comments` loops, you use `.get()` for the `if` condition but direct key access (e.g., `p["title"]`) for the `append` call. If the key is missing, the program will raise a `KeyError`. Use `.get()` consistently.
* **Nested Conditionals:** The result count logic in `main()` is deeply nested. Use `elif` statements to flatten the structure and improve readability.

**Performance & Security**
* **Error Handling:** Catching a generic `Exception` is too broad. Use `requests.exceptions.RequestException` to handle network-specific errors specifically.
* **Response Validation:** The code calls `.json()` without checking if the HTTP request was successful. Add `response.raise_for_status()` before parsing the JSON.

**Suggested Improvements Summary**
* Create a helper function for API requests.
* Replace global variables with function return values.
* Use `elif` for the result range checks.
* Ensure consistent use of `.get()` when accessing dictionary keys.