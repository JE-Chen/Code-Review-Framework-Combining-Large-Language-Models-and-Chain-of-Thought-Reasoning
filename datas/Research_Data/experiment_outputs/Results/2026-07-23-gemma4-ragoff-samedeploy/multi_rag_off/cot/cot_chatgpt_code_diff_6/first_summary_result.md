### Code Review

#### 1. Readability & Consistency
- **Formatting**: The code follows PEP 8 standards generally well.
- **Consistency**: The use of a global `SESSION` object is consistent, though its lifecycle management in `main()` is a bit fragile.

#### 2. Naming Conventions
- **Descriptive Names**: `get_something` and `do_network_logic` are overly generic. They should be renamed to reflect the actual business purpose (e.g., `fetch_endpoint_data` and `execute_fetch_cycle`).

#### 3. Software Engineering Standards
- **Modularity**: The logic is split into functions, which is good. However, the `SESSION` is a global variable, making the functions harder to unit test in isolation without mocking the global state.
- **Abstraction**: The URL construction `BASE_URL + endpoint + ...` is brittle. Using `requests` params dictionary or `urllib.parse` is preferred.

#### 4. Logic & Correctness
- **Inconsistent Return Types**: `parse_response` returns a dictionary on HTTP error, a string on JSON parsing failure, and a formatted string on success. This forces the caller to handle multiple types, which is error-prone.
- **Unstable Timeout**: In `get_something`, the timeout is randomly applied. This introduces non-deterministic behavior that will make debugging production latency or timeout issues nearly impossible.
- **Broad Exception Handling**: `except Exception:` in `parse_response` and `main` catches everything (including `KeyboardInterrupt` in some Python versions). It should catch specific exceptions (e.g., `requests.exceptions.RequestException`, `ValueError`).

#### 5. Performance & Security
- **Resource Management**: While `SESSION.close()` is called in `main`, it is not wrapped in a `finally` block. If an exception occurs before the close call, the session remains open.
- **Input Validation**: `kind` is passed directly into the URL string. While it is currently controlled by a random list, if this were to ever accept user input, it would be vulnerable to parameter injection.

#### 6. Documentation & Testing
- **Missing Documentation**: There are no docstrings explaining the purpose of the functions or the expected return types.
- **Testing**: No unit tests are provided for the parsing logic or the network wrapper.

---

### Summary of Recommendations

| Severity | Issue | Recommendation |
| :--- | :--- | :--- |
| **High** | Inconsistent return types in `parse_response` | Standardize return type (e.g., always a dict or raise a custom exception). |
| **High** | Non-deterministic timeout logic | Remove `random.choice` for timeouts; use a consistent, defined timeout value. |
| **Medium** | Global Session state | Pass the session as an argument to functions to improve testability. |
| **Medium** | Broad `except Exception` | Replace with specific exception types (e.g., `json.JSONDecodeError`). |
| **Low** | Generic naming | Rename `get_something` and `do_network_logic` to be more descriptive. |