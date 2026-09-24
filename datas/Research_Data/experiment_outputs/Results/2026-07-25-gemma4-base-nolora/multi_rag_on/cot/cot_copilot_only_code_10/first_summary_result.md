### PR Summary

*   **Key changes**: Implemented an `APIClient` to fetch data from a JSON placeholder API and a processing pipeline to filter users, posts, and todos.
*   **Purpose of changes**: Establish a basic data retrieval and filtering mechanism for external API integration.
*   **Items to confirm**: Review the error handling strategy in `APIClient.fetch` and the use of a global cache.

---

### Code Review

#### 1. Readability & Consistency
*   **Formatting**: The code generally follows PEP 8; however, the nested `if/else` blocks in `main()` are unnecessarily deep and reduce readability.

#### 2. Naming Conventions
*   **Variable Names**: In `process_all()`, the variables `u`, `p`, and `t` are too concise. They should be renamed to `user`, `post`, and `todo` to maintain semantic clarity.

#### 3. Software Engineering Standards
*   **Duplicate Code**: The functions `get_users`, `get_posts`, and `get_todos` are nearly identical. This is a violation of the DRY (Don't Repeat Yourself) principle.
    *   *Recommendation*: Create a generic `get_resource(client, endpoint, cache_key)` function.
*   **Modularity**: The `APIClient` is a good start, but the dependency on a global `SESSION` object makes the class less portable and harder to test in isolation.

#### 4. Logic & Correctness
*   **Error Handling**: The `fetch` method catches all exceptions (`Exception as e`) and returns them as a dictionary. This masks the difference between a network failure and a logic error, and it forces the caller to check for an `"error"` key in the returned data.
*   **Boundary Conditions**: In `process_all()`, the code iterates over `users`, `posts`, and `todos`. If `fetch` returns an error dictionary (e.g., `{"error": "..."}`), the subsequent `for` loops will attempt to iterate over the keys of that dictionary rather than a list of items, likely leading to unexpected behavior or crashes when calling `.get()` on strings.

#### 5. Performance & Security
*   **Global State**: The use of `GLOBAL_CACHE` is problematic. It is populated but never read from, making it currently useless. If intended for future use, it should be encapsulated within a class or a dedicated cache manager to avoid side effects across different parts of the application.
*   **String Concatenation**: The code uses `+` for string concatenation (e.g., `"Bad status: " + str(response.status_code)`). While acceptable for small scripts, f-strings are preferred for performance and readability.

#### 6. Documentation & Testing
*   **Missing Tests**: There are no unit tests provided for the `APIClient` or the processing logic.
*   **Documentation**: The code lacks docstrings for classes and functions, making it difficult to understand the expected input/output types.

### Summary of Suggested Refactorings
1.  **Flatten `main()`**: Use `elif` instead of nested `if/else`.
2.  **Generic Fetcher**: Replace the three `get_x` functions with one parameterized function.
3.  **Type Validation**: Ensure `fetch` returns a consistent type (e.g., always a list or raise a custom exception) so that `process_all` doesn't iterate over error messages.
4.  **Rename Iterators**: Change `u, p, t` $\rightarrow$ `user, post, todo`.