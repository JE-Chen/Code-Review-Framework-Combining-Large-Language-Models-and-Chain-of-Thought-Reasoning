### Code Review Summary

#### 1. **Readability & Consistency**
- **Indentation & Formatting**: Indentation is consistent and readable.
- **Comments**: No inline comments; could benefit from brief docstrings or comments for functions to explain their purpose.

#### 2. **Naming Conventions**
- **Variable Names**: 
  - `u`, `p`, `c` are too generic — consider more descriptive names like `user`, `post`, `comment`.
- **Function Names**:
  - Function names (`get_users`, `get_posts`, etc.) are clear and follow naming conventions.
- **Global Variable**:
  - `GLOBAL_RESULTS` is capitalized but used as a mutable global state, which can reduce modularity and testability.

#### 3. **Software Engineering Standards**
- **Duplicate Code**:
  - The pattern of fetching data with error handling is repeated across `get_users`, `get_posts`, and `get_comments`. Consider abstracting into a reusable helper function.
- **Modularity**:
  - Logic is mixed in `process_data()` and `main()`. Separating concerns would improve maintainability.
- **Global State**:
  - Using `GLOBAL_RESULTS` makes the code harder to test and reuse. Prefer returning values instead of mutating a global list.

#### 4. **Logic & Correctness**
- **Error Handling**:
  - Generic `except Exception as e:` is not ideal. It's better to catch specific exceptions (e.g., `requests.RequestException`) for clearer debugging.
- **Boundary Conditions**:
  - No explicit checks for empty responses or invalid JSON. If the API returns malformed data, it might cause runtime errors.
- **Conditional Logic**:
  - Nested conditionals in `main()` for result counts can be simplified using `elif`.

#### 5. **Performance & Security**
- **Performance**:
  - No major bottlenecks visible, but repeated API calls may affect performance if scaled.
- **Security**:
  - No direct security risks detected in this snippet. However, ensure that `BASE_URL` is validated if dynamically set.

#### 6. **Documentation & Testing**
- **Documentation**:
  - Missing docstrings or inline comments explaining what each function does.
- **Testing**:
  - No unit tests provided. Functions should be made testable by removing side effects (like printing and global mutation).

#### 7. **Suggestions for Improvement**

- ✅ Replace `u`, `p`, `c` with `user`, `post`, `comment` in loops for clarity.
- ✅ Refactor repeated request logic into a single helper function.
- ✅ Avoid using `GLOBAL_RESULTS`—return results from `process_data()` instead.
- ✅ Improve error handling with specific exceptions (e.g., `requests.RequestException`).
- ✅ Simplify nested `if` statements in `main()` using `elif`.
- ✅ Add docstrings or comments to clarify functionality of each function.
- ✅ Add unit tests to verify behavior without side effects.

--- 

This review focuses on key structural and maintainability improvements while avoiding over-engineering.