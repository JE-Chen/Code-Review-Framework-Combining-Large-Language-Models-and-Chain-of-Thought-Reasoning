### Code Review

**Naming Conventions**
*   `get_something`: The function name is too vague. Suggest `fetch_data` or `get_endpoint_data` to better describe its purpose.
*   `kind`: In the context of a URL parameter, `param_type` or `category` would be more descriptive.

**Logic & Correctness**
*   **Inconsistent Return Types**: `parse_response` returns a dictionary on HTTP error, a string on JSON parsing failure, and a formatted string on success. This will likely cause `TypeError` or unexpected behavior in the calling function. Suggest returning a consistent type (e.g., always a dictionary or always a string).
*   **Unstable Timeout**: `get_something` randomly applies a 1-second timeout to some requests but no timeout to others. This can lead to the application hanging indefinitely if the server doesn't respond. Suggest applying a consistent timeout to all requests.
*   **Broad Exception Handling**: `except Exception:` in `parse_response` and `main` is too broad. It can hide critical bugs (like `KeyboardInterrupt` or `MemoryError`). Suggest catching specific exceptions (e.g., `requests.exceptions.RequestException`, `ValueError`).

**Software Engineering Standards**
*   **String Concatenation**: The URL construction `BASE_URL + endpoint + ...` is brittle. Suggest using `requests` built-in `params` argument: `SESSION.get(url, params={"type": kind})`.

**Performance & Security**
*   **Resource Management**: While `SESSION.close()` is called in `main`, it is safer to use a `with requests.Session() as session:` block to ensure the connection is closed even if an unhandled exception occurs.

**Documentation**
*   The file lacks docstrings for functions, making it difficult to understand the expected input/output of the network logic.