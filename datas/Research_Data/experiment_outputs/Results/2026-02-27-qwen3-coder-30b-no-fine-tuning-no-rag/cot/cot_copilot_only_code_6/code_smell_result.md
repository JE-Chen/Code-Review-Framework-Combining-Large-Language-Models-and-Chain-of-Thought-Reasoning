### Code Smell Type: Global State Usage
- **Problem Location:** `DATA_STORE`, `USER_COUNT`, `CONFIG` are defined globally at module level.
- **Detailed Explanation:** Using global variables makes the application harder to reason about, debug, and test. It introduces tight coupling between functions and can lead to race conditions or unexpected behavior when multiple threads or requests interact with shared mutable state.
- **Improvement Suggestions:** Replace global state with a proper data store (like a class-based service or database). If using globals is necessary for simplicity (e.g., during prototyping), encapsulate them in a dedicated module or class to minimize side effects.
- **Priority Level:** High

---

### Code Smell Type: Magic Numbers/Strings
- **Problem Location:** In `/items` route, `CONFIG["threshold"]` is hardcoded to `123`. In `/complex` route, values like `"test"` and `"reset"` are used directly.
- **Detailed Explanation:** Magic strings and numbers reduce code clarity and make future changes difficult. They don't convey meaning without external context and increase the risk of inconsistencies if changed in one place but not others.
- **Improvement Suggestions:** Define constants for these values (e.g., `THRESHOLD = 123`, `MODE_TEST = "test"`). This improves readability and allows centralized configuration management.
- **Priority Level:** Medium

---

### Code Smell Type: Long Function
- **Problem Location:** The `/complex` route function (`complex_route`) contains deeply nested conditional logic.
- **Detailed Explanation:** The function has high cyclomatic complexity due to multiple nested `if` statements. This reduces readability, increases testing difficulty, and makes debugging more error-prone. It violates the Single Responsibility Principle by handling too many different cases within a single function.
- **Improvement Suggestions:** Extract logic into smaller helper functions or use a dictionary-based lookup for parameter handling. For example, create a mapping from parameters to actions.
- **Priority Level:** High

---

### Code Smell Type: Poor Exception Handling
- **Problem Location:** In `/add` route, generic `except Exception as e:` catches all exceptions.
- **Detailed Explanation:** Catching broad exceptions hides underlying issues and prevents proper error propagation. This makes troubleshooting harder and can mask critical bugs or security vulnerabilities.
- **Improvement Suggestions:** Catch specific exceptions such as `ValueError`, `TypeError`, or custom exceptions. Log errors appropriately and return informative error messages only when needed.
- **Priority Level:** High

---

### Code Smell Type: Inconsistent Naming Conventions
- **Problem Location:** Mix of snake_case and camelCase (e.g., `USER_COUNT`, `DATA_STORE`, `CONFIG` vs. `add_item`, `get_items`).
- **Detailed Explanation:** Inconsistent naming breaks developer expectations and makes the codebase feel disorganized. While not strictly wrong, it impacts maintainability and onboarding speed for new developers.
- **Improvement Suggestions:** Standardize on snake_case for variable and function names throughout the project to align with Python conventions.
- **Priority Level:** Medium

---

### Code Smell Type: Lack of Input Validation
- **Problem Location:** No validation on incoming JSON payload (`request.json.get("item")`) or query parameters (`request.args.get("param")`).
- **Detailed Explanation:** Without validating inputs, the application becomes vulnerable to malformed data or malicious payloads. This could result in runtime errors, incorrect behavior, or even injection attacks depending on how data is processed downstream.
- **Improvement Suggestions:** Add input validation checks before processing any user-provided data. Use libraries like `marshmallow` or `pydantic` for schema validation where appropriate.
- **Priority Level:** High

---

### Code Smell Type: Violation of Single Responsibility Principle
- **Problem Location:** The `/reset` endpoint modifies both `DATA_STORE` and `CONFIG`.
- **Detailed Explanation:** This endpoint does two unrelated things — resetting data and changing mode settings — violating the SRP. Future modifications might affect one part unintentionally.
- **Improvement Suggestions:** Split responsibilities: have separate endpoints for resetting data and updating config. Alternatively, encapsulate each operation in its own function/module.
- **Priority Level:** Medium

---

### Code Smell Type: Hardcoded Behavior Based on Mode
- **Problem Location:** Logic inside `/items` route that changes based on `CONFIG["mode"]`.
- **Detailed Explanation:** Hardcoding behavior based on configuration flags leads to tightly coupled logic. It's hard to extend or change modes without touching core logic, reducing flexibility and testability.
- **Improvement Suggestions:** Introduce strategy patterns or switch-case structures to dynamically choose processing logic based on mode rather than hardcoding it.
- **Priority Level:** Medium

---

### Code Smell Type: Lack of Documentation
- **Problem Location:** Missing docstrings and inline comments explaining the purpose of routes and logic.
- **Detailed Explanation:** Without documentation, other developers struggle to understand the intent behind certain behaviors, especially in complex or ambiguous code paths. This slows down collaboration and maintenance.
- **Improvement Suggestions:** Add docstrings to functions and inline comments where logic isn’t obvious. Consider documenting API endpoints with Swagger/OpenAPI specs.
- **Priority Level:** Medium

---

### Code Smell Type: Duplicated Logic
- **Problem Location:** The pattern of returning `{"id": i, "value": item}` appears twice in `/items`.
- **Detailed Explanation:** While not exactly duplicated, similar structures are repeated unnecessarily. Refactoring would improve consistency and reduce redundancy.
- **Improvement Suggestions:** Create a reusable function to format items with ID and value. This helps avoid duplication and ensures consistent output formatting.
- **Priority Level:** Low

---

### Code Smell Type: Unnecessary Complexity in Route Definitions
- **Problem Location:** `/complex` route uses excessive nesting and branching.
- **Detailed Explanation:** Deeply nested control flow makes understanding the code path challenging. This kind of structure can be simplified using early returns or lookup tables.
- **Improvement Suggestions:** Restructure using guard clauses or mapping strategies to flatten the conditional logic.
- **Priority Level:** Medium

---