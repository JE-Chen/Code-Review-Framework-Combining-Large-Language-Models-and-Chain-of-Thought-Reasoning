### Code Review

**Logic & Correctness**
* **Inconsistent Timeout:** In `get_something`, the `timeout` is applied randomly. This leads to non-deterministic behavior where some requests may hang indefinitely while others fail quickly.
* **Broad Exception Handling:** `parse_response` and `main` use `except Exception:`. This hides specific errors (like `requests.exceptions.RequestException` or `json.JSONDecodeError`) and makes debugging difficult.

**Naming Conventions**
* **Vague Naming:** `get_something` and `do_network_logic` are non-descriptive. Use names that reflect the actual purpose (e.g., `fetch_data` and `execute_fetch_cycle`).

**Software Engineering Standards**
* **Shared Mutable State:** `SESSION` is defined as a global object. This can lead to hidden coupling and makes unit testing difficult. Pass the session as an argument to functions.
* **Hard-coded Logic:** The `0.05` and `0.1` values in `do_network_logic` are magic numbers. Move these to named constants.

**Readability & Consistency**
* **String Concatenation:** In `get_something`, the URL is built using `+`. Use f-strings or `requests` params argument for better readability and safety.
* **Inconsistent Return Types:** `parse_response` returns a dictionary on error, a string on JSON failure, and a formatted string on success. This forces the caller to handle multiple types, increasing complexity.

**Suggestions for Improvement**
* Use `requests.get(url, params={"type": kind})` instead of manual string concatenation.
* Replace `except Exception:` with specific exceptions (e.g., `requests.exceptions.Timeout`).
* Encapsulate the `requests.Session()` within a context manager or pass it as a dependency.