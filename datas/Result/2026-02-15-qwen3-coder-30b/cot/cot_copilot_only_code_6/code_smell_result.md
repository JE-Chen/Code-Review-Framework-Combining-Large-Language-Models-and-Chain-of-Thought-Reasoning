### Code Smell Type: Global State Usage
- **Problem Location**: `DATA_STORE`, `USER_COUNT`, `CONFIG` declared at module level.
- **Detailed Explanation**: The use of global variables makes the application state unpredictable and hard to manage. It violates encapsulation principles and introduces side effects that are difficult to trace during testing or deployment.
- **Improvement Suggestions**: Replace globals with a proper data store object or service class. Use dependency injection where possible to make dependencies explicit.
- **Priority Level**: High

---

### Code Smell Type: Magic Numbers/Strings
- **Problem Location**: `"test"` string in `get_items()` and threshold value `123`.
- **Detailed Explanation**: These hardcoded values reduce flexibility and readability. If they need to change later, you must update them in multiple places without clear indication of their purpose.
- **Improvement Suggestions**: Extract these into constants with descriptive names (`TEST_MODE`, `DEFAULT_THRESHOLD`) defined at the top of the file or in a config module.
- **Priority Level**: Medium

---

### Code Smell Type: Long Function / Complex Control Flow
- **Problem Location**: `/complex` route contains deeply nested conditional blocks.
- **Detailed Explanation**: The nested `if` statements make the logic hard to follow and increase the risk of errors when modifying. This reduces maintainability and readability.
- **Improvement Suggestions**: Refactor using early returns, helper functions, or a switch-like structure (e.g., mapping parameters to handlers). Break down logic into smaller, focused units.
- **Priority Level**: High

---

### Code Smell Type: Lack of Input Validation
- **Problem Location**: No validation on input from `request.json`.
- **Detailed Explanation**: There's no check whether the incoming JSON contains required fields or valid types. This can lead to runtime exceptions or unexpected behavior.
- **Improvement Suggestions**: Add schema validation (using libraries like Marshmallow or Pydantic), validate required keys before processing, and handle missing or malformed inputs gracefully.
- **Priority Level**: High

---

### Code Smell Type: Violation of Single Responsibility Principle
- **Problem Location**: `get_items()` handles both filtering and transformation based on mode.
- **Detailed Explanation**: A single function should ideally do one thing well. Mixing concerns here makes it harder to reason about its behavior and test it effectively.
- **Improvement Suggestions**: Split responsibilities: separate filtering logic from transformation logic into distinct functions or classes.
- **Priority Level**: Medium

---

### Code Smell Type: Poor Error Handling
- **Problem Location**: Generic `except Exception as e:` in `add_item()`.
- **Detailed Explanation**: Catching broad exceptions hides real issues and prevents proper error propagation. It also provides little insight into debugging failures.
- **Improvement Suggestions**: Catch specific exceptions and log meaningful error messages. Consider raising custom exceptions for clearer communication.
- **Priority Level**: Medium

---

### Code Smell Type: Hardcoded Behavior Based on Mode
- **Problem Location**: Conditional logic in `get_items()` depending on `CONFIG["mode"]`.
- **Detailed Explanation**: The mode field acts as a flag that alters behavior arbitrarily. This design makes the system brittle and harder to extend or test in isolation.
- **Priority Level**: Medium

---

### Code Smell Type: Inconsistent Naming
- **Problem Location**: Mix of camelCase and snake_case for variables such as `USER_COUNT` vs `CONFIG`.
- **Detailed Explanation**: Inconsistent naming hinders understanding of the codebase and violates common Python conventions (PEP8 suggests snake_case).
- **Improvement Suggestions**: Standardize naming conventions across the project—prefer snake_case for variables and functions.
- **Priority Level**: Low

---

### Code Smell Type: Missing Unit Tests
- **Problem Location**: No test files included.
- **Detailed Explanation**: Without tests, changes risk breaking existing functionality silently. Tests ensure correctness and facilitate refactoring.
- **Improvement Suggestions**: Create unit tests for each endpoint covering success cases, edge cases, and error paths.
- **Priority Level**: Medium

---

### Code Smell Type: Security Risk via Mutable Configuration
- **Problem Location**: Direct modification of `CONFIG["mode"]` inside `reset_data()`.
- **Detailed Explanation**: Allowing arbitrary writes to configuration can introduce vulnerabilities or instability if not properly controlled.
- **Improvement Suggestions**: Make config immutable or provide a secure interface for updates only under controlled conditions.
- **Priority Level**: Medium