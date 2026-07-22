### Code Review

#### 1. Readability & Consistency
- **Formatting**: The code is generally well-formatted and follows PEP 8 standards.
- **Consistency**: The use of whitespace and indentation is consistent throughout the file.

#### 2. Naming Conventions
- **Variable Naming**: `GLOBAL_THING` is too generic and non-descriptive. It should be renamed to reflect its purpose (e.g., `AppState` or `SessionData`).
- **Method Naming**: `do_periodic_stuff` and `compute_title` are vague. More descriptive names like `update_ui_randomly` or `update_window_title` would improve semantic clarity.

#### 3. Software Engineering Standards
- **State Management**: The use of a global dictionary (`GLOBAL_THING`) for application state is a poor practice. This state should be encapsulated within the `MyWindow` class or a dedicated State Manager class to improve testability and maintainability.
- **Modularity**: The logic for generating text and computing titles is mixed with UI updates. Separating the business logic from the view would make the code more modular.

#### 4. Logic & Correctness
- **Blocking the UI Thread**: In `handle_click`, `time.sleep(0.1)` is called on the main GUI thread. While 100ms is short, calling `sleep` in a PySide/PyQt application freezes the event loop, which can lead to unresponsive interfaces. Use `QTimer` or asynchronous patterns if delays are necessary.
- **State Mutation in Getter**: `compute_title` is named like a getter/calculator but it modifies the global state (`GLOBAL_THING["mood"] = ...`). This is a side effect that makes the code harder to debug.

#### 5. Performance & Security
- **Performance**: No significant bottlenecks identified for a script of this scale.
- **Security**: No external inputs are processed, so there are no immediate security risks.

#### 6. Documentation & Testing
- **Documentation**: The code lacks docstrings for the class and its methods.
- **Testing**: No unit tests are provided. The current structure (global state) makes writing isolated unit tests difficult.

---

### Summary of Recommendations
1. **Refactor State**: Move `GLOBAL_THING` into a class instance.
2. **Remove `time.sleep`**: Eliminate blocking calls from the main thread.
3. **Improve Naming**: Rename generic variables and methods to be more descriptive.
4. **Separate Concerns**: Ensure methods that "compute" or "generate" values do not also modify the application state.