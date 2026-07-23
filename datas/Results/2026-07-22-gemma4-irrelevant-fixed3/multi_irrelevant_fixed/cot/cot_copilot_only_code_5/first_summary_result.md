### Code Review

#### 1. Readability & Consistency
- **Formatting**: The code is well-formatted and follows standard Python indentation and spacing.
- **Consistency**: The style is consistent throughout the file.

#### 2. Naming Conventions
- **Naming**: Variable and function names (`init_data`, `process_items`, `GLOBAL_STATE`) are descriptive and follow standard naming conventions.

#### 3. Software Engineering Standards
- **Modularization**: The logic is split into functions, but the heavy reliance on a global dictionary (`GLOBAL_STATE`) creates tight coupling.
- **Maintainability**: Using a global state makes the code harder to test in isolation and can lead to side-effect bugs as the project grows. 
- **Recommendation**: Consider encapsulating the state within a class (e.g., `StateManager`) to avoid global mutations.

#### 4. Logic & Correctness
- **Correctness**: The logic for `process_items` and state transitions is correct based on the current implementation.
- **Boundary Conditions**: The `threshold` logic in `process_items` handles values above and below the threshold correctly.

#### 5. Performance & Security
- **Performance**: The time complexity of `process_items` is $O(n)$, which is optimal for this operation.
- **Security**: No external inputs are processed, so there are no immediate security vulnerabilities.

#### 6. Documentation & Testing
- **Documentation**: The code lacks docstrings. While the functions are simple, adding brief descriptions of the expected behavior of `process_items` would improve clarity.
- **Testing**: There are no unit tests provided; the `main()` function serves as a basic manual smoke test.

---

### PR Summary

- **Key changes**: Implemented a global state management system with functions to initialize, modify, and process data based on conditional flags and thresholds.
- **Impact scope**: Affects the core state handling and data processing logic.
- **Purpose of changes**: Establish a basic framework for state-dependent data transformation.
- **Items to confirm**: Verify if the global state pattern is acceptable for the project's scale or if a class-based approach is preferred.