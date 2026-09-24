1. **Overall conclusion**
   - The PR does **not** meet merge criteria.
   - There are critical blocking concerns regarding UI responsiveness and architectural flaws (global state management) that must be addressed before merging.

2. **Comprehensive evaluation**
   - **Code Quality and Correctness**: The implementation contains a critical bug where `time.sleep(0.1)` is called on the main GUI thread within `handle_click`, which freezes the event loop. Additionally, `compute_title` violates command-query separation by modifying global state while returning a value.
   - **Maintainability and Design**: The use of a mutable global dictionary (`GLOBAL_THING`) creates tight coupling and hinders testability. The design lacks modularity, mixing business logic (state updates) directly with UI logic. There is a total absence of docstrings and unit tests.
   - **Consistency and Standards**: While the code follows PEP 8 formatting, it fails naming standards with vague identifiers (`GLOBAL_THING`, `do_periodic_stuff`). The use of "magic numbers" (e.g., 777, 0.3, 7) without named constants makes the logic opaque.

3. **Final decision recommendation**
   - **Request changes**
   - **Justification**: The combination of a blocking UI thread (Error), high-priority architectural smells (Global State), and poor naming conventions requires a refactor to ensure the application is stable, maintainable, and professional.

4. **Team follow-up**
   - **Refactor State**: Encapsulate `GLOBAL_THING` into a dedicated `AppState` class or move it into `MyWindow` as instance attributes.
   - **Fix UI Blocking**: Remove `time.sleep()` from the main thread; use `QTimer` if a delay is necessary.
   - **Clean up Naming**: Rename `GLOBAL_THING`, `do_periodic_stuff`, and `compute_title` to be descriptive.
   - **Extract Constants**: Replace magic numbers (777, 0.3, 7) with named constants.
   - **Separate Concerns**: Move state mutation logic out of the `compute_title` getter.