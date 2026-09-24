### Pull Request Summary

*   **Key changes**: Implemented a data retrieval and processing pipeline that fetches users, posts, and comments from an external API and filters them based on specific criteria.
*   **Impact scope**: New implementation involving network requests and data processing logic.
*   **Purpose of changes**: Feature addition to aggregate and categorize specific data points from the JSONPlaceholder API.
*   **Items to confirm**: Review the error handling strategy and the use of global state for result accumulation.

---

### Code Review

#### 1. Logic & Correctness
*   **Potential Runtime Error**: In `process_data`, the code uses `p["title"]` and `c["email"]` after checking for their existence using `.get()`. If the key is missing, the `.get()` check passes (returning an empty string), but the subsequent access `p["title"]` will raise a `KeyError`.
    *   *Recommendation*: Use the variable returned by `.get()` or ensure the key exists before direct access.

#### 2. Software Engineering Standards
*   **Shared Mutable State**: The use of `GLOBAL_RESULTS = []` at the module level introduces hidden coupling. This makes the code harder to test and prevents `process_data` from being called multiple times without manually clearing the list.
    *   *Recommendation*: Have `process_data` return a list of results and pass that list to the printing logic.
*   **Modularization**: The `get_` functions (`get_users`, `get_posts`, `get_comments`) are nearly identical.
    *   *Recommendation*: Create a single generic `fetch_data(endpoint)` function to reduce duplication.

#### 3. Performance & Security
*   **Input Validation**: While the API is trusted in this example, the code lacks validation of the response status code. `response.json()` will be called even if the server returns a 404 or 500 error.
    *   *Recommendation*: Call `response.raise_for_status()` before parsing JSON.

#### 4. RAG Rule Violations
*   **Broad Exception Handling**: All `get_` functions use `except Exception as e:`. This catches everything, including `KeyboardInterrupt` or `SystemExit`, and hides the specific nature of the failure (e.g., connection timeout vs. JSON decoding error).
    *   *Recommendation*: Catch specific exceptions like `requests.RequestException`.
*   **Deeply Nested Conditionals**: The `main()` function contains deeply nested `if/else` blocks to categorize the result count.
    *   *Recommendation*: Use guard clauses or a more linear structure to reduce cognitive load.
*   **Implicit Truthiness**: The check `if len(GLOBAL_RESULTS) > 0:` is used.
    *   *Recommendation*: While common in Python, for complex logic, explicit comparisons or simply `if GLOBAL_RESULTS:` (if following Pythonic truthiness) is preferred, but the RAG rule suggests avoiding implicit truthiness for complex objects to improve clarity.
*   **Single Responsibility Principle**: `process_data` is responsible for coordinating three different API calls and applying three different sets of business logic.
    *   *Recommendation*: Split the filtering logic into separate functions (e.g., `filter_users`, `filter_posts`).

#### 5. Readability & Consistency
*   **Naming**: Variable names like `u`, `p`, and `c` in loops are too short and ambiguous.
    *   *Recommendation*: Use `user`, `post`, and `comment`.