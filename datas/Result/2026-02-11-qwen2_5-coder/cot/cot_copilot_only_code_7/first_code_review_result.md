- **Indentation**: Proper indentation is used, but consider using an IDE's auto-formatting feature to enforce consistent style.
- **Comments**: Comments are minimal. Add comments explaining non-obvious logic or complex operations.
- **Naming Conventions**:
  - `GLOBAL_TEXT`, `GLOBAL_COUNTER`, `GLOBAL_MODE` could be more descriptive.
  - Method names like `handle_btn1`, `handle_btn2`, `handle_btn3` are clear but can use more context-specific names.
- **Clarity**:
  - Global variables are used extensively, which makes the code harder to reason about and test. Encourage encapsulation.
  - The purpose of some buttons and their interactions could be better documented.
- **Modularity**:
  - The GUI components and logic are tightly coupled. Consider separating concerns into different classes or modules.
- **Logic & Correctness**:
  - The use of global variables increases coupling and makes it hard to track state changes. Use local variables or pass state through methods.
  - Exception handling is missing, especially for UI interactions.
- **Performance**:
  - Appending to `QTextEdit` repeatedly without clearing can lead to performance issues. Consider batch updates or periodic clears.
- **Security**:
  - Input validation is minimal. Consider validating user inputs, especially if they affect application behavior.
- **Documentation**:
  - Add docstrings to functions and classes to explain their purpose and parameters.
  - Include README or inline comments explaining the application's functionality and how to run it.
- **Testing**:
  - Unit tests for individual components would help catch regressions and ensure future changes don't break existing features.

### Suggestions
1. Refactor global variables into instance variables or pass them as arguments.
2. Use enums or constants instead of magic strings (`"default"`, `"reset"`).
3. Implement proper error handling, especially for UI interactions.
4. Break down the `MainWindow` class into smaller, more focused classes.
5. Document each method and add comments where needed.