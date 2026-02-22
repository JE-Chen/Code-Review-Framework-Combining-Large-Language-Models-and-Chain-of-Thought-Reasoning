### Code Review Summary

- **Readability & Consistency**: Indentation and structure are acceptable but could benefit from consistent spacing and clearer comments.
- **Naming Conventions**: Function and variable names are somewhat generic; more descriptive names would improve clarity.
- **Software Engineering Standards**: Logic can be simplified by reducing randomness and duplication.
- **Logic & Correctness**: Minor edge cases like empty JSON responses may lead to silent failures.
- **Performance & Security**: No major performance or security issues, but session usage and timeouts could be improved.
- **Documentation & Testing**: Minimal documentation or testing present; adding docstrings and unit tests is recommended.

---

### Suggestions

- **Function Names**:
  - Rename `get_something` to something more specific like `fetch_data_by_type`.
  - Consider renaming `do_network_logic` to `process_fetch_requests`.

- **Error Handling**:
  - Replace broad exception catching (`except Exception:`) with specific exceptions.
  - Improve error reporting in `parse_response()` instead of returning a string.

- **Randomness & Control**:
  - Remove unnecessary randomness (`random.choice`, `random.randint`) for better reproducibility.

- **Code Duplication**:
  - Abstract common patterns like HTTP request handling into reusable components.

- **Session Management**:
  - Use context managers (`with` statement) for cleaner session lifecycle handling.

- **Comments & Docstrings**:
  - Add inline comments explaining why certain behaviors exist (e.g., sleep logic).
  - Include basic docstrings for functions.

- **Testing**:
  - Write unit tests for `parse_response` and `do_network_logic` to validate behavior under various inputs.

---