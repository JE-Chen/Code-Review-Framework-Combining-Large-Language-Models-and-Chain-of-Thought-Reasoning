### Code Review Summary

#### 1. **Readability & Consistency**
- **Indentation & Formatting**: Indentation is consistent, but consider using a linter/formatter like `black` or `autopep8` for uniformity.
- **Comments**: No inline comments are present; adding brief descriptions to methods can improve clarity.

#### 2. **Naming Conventions**
- **Global Variables**: Names like `GLOBAL_TEXT`, `GLOBAL_COUNTER`, and `GLOBAL_MODE` are not descriptive enough. Consider renaming them to reflect their purpose (e.g., `text_buffer`, `click_count`, `mode_state`).
- **Function Names**: Function names (`handle_btn1`, `handle_btn2`) are too generic. Use more descriptive names like `add_text_to_buffer`, `display_counter_status`, `reset_application_state`.

#### 3. **Software Engineering Standards**
- **Use of Global Variables**: Heavy reliance on global variables reduces modularity and makes testing harder. Refactor into instance attributes or a dedicated model class.
- **Duplicate Logic**: The same condition checks in `handle_btn2` could be simplified for better readability.
- **Lack of Modularity**: The UI logic and state management are tightly coupled. Consider separating concerns by creating a data model and updating UI based on model changes.

#### 4. **Logic & Correctness**
- **Boundary Conditions**: In `handle_btn1`, empty input detection works, but no validation for special characters or max length is implemented.
- **Mode Handling**: `GLOBAL_MODE` is used inconsistently—its role is unclear and may lead to unexpected behavior.

#### 5. **Performance & Security**
- **No Performance Bottlenecks Detected**: No major inefficiencies found in current implementation.
- **Security Risks**: No user input sanitization is performed. If used in production, consider validating/sanitizing inputs to prevent injection attacks or unintended behavior.

#### 6. **Documentation & Testing**
- **Missing Documentation**: There are no docstrings or inline comments explaining what each method does.
- **Testing Gap**: No unit tests exist. Add tests for `handle_btn1`, `handle_btn2`, and `handle_btn3` with various inputs and states.

#### 7. **Suggestions for Improvement**
- Replace global variables with instance attributes.
- Rename functions and variables for clarity.
- Implement proper separation of logic and UI.
- Add basic input validation and error handling.
- Include docstrings and unit tests for future maintainability.