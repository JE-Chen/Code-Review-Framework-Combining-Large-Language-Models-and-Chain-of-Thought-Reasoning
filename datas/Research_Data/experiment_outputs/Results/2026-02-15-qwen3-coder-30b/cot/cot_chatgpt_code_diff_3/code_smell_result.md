### Code Smell Type: Global State Usage
- **Problem Location:** `GLOBAL_THING` variable declared at module level and accessed/modified by multiple methods.
- **Detailed Explanation:** The use of a global mutable state makes the system hard to reason about, introduces tight coupling between components, and can lead to unpredictable behavior when changes occur elsewhere in the application. It also hinders testing because dependencies on external state are not explicit.
- **Improvement Suggestions:** Replace `GLOBAL_THING` with an instance attribute or encapsulate it into a dedicated class that manages internal state. This promotes encapsulation and allows for easier mocking during tests.
- **Priority Level:** High

---

### Code Smell Type: Magic Number
- **Problem Location:** Timer interval `777`, sleep duration `0.1`, and modulo operations like `% 5` and `% 7`.
- **Detailed Explanation:** Magic numbers reduce readability and make future maintenance difficult. If these values need to be changed or explained, developers must guess their purpose without context.
- **Improvement Suggestions:** Define constants for all such values (`TIMER_INTERVAL`, `SLEEP_DURATION`, etc.) and document their purpose. Use descriptive names instead of arbitrary integers.
- **Priority Level:** Medium

---

### Code Smell Type: Side Effects in Pure Functions
- **Problem Location:** `compute_title()` modifies `GLOBAL_THING["mood"]` inside its body.
- **Detailed Explanation:** A pure function should not have side effects. Modifying global state from within a method labeled as a “computation” leads to confusion and reduces predictability.
- **Improvement Suggestions:** Separate concerns: `compute_title()` should only return a string based on current inputs, while updating the global mood should happen elsewhere explicitly.
- **Priority Level:** High

---

### Code Smell Type: Long Function
- **Problem Location:** `handle_click()` and `do_periodic_stuff()` both perform multiple unrelated actions.
- **Detailed Explanation:** These functions violate the Single Responsibility Principle (SRP). They manage UI updates, logic flow, and state transitions all at once, making them harder to read, debug, and test independently.
- **Improvement Suggestions:** Decompose each function into smaller helper methods responsible for one clear task—e.g., updating click count, triggering UI changes, managing mood updates.
- **Priority Level:** Medium

---

### Code Smell Type: Inconsistent Naming Convention
- **Problem Location:** Mix of camelCase (`handle_click`) and snake_case (`compute_title`) for function names.
- **Detailed Explanation:** Inconsistent naming makes the codebase harder to navigate and understand, especially when working across teams where naming standards vary.
- **Improvement Suggestions:** Standardize on either snake_case or camelCase throughout the codebase. Prefer snake_case for Python (PEP8).
- **Priority Level:** Low

---

### Code Smell Type: Lack of Input Validation
- **Problem Location:** No checks on `GLOBAL_THING` contents or user input validity.
- **Detailed Explanation:** There’s no safeguard against malformed or unexpected data in the global dictionary, which could crash or misbehave the app under edge cases.
- **Improvement Suggestions:** Add defensive programming practices like type checking or default fallbacks for critical fields in `GLOBAL_THING`.
- **Priority Level:** Medium

---

### Code Smell Type: Tight Coupling Between Components
- **Problem Location:** Direct access to `GLOBAL_THING` across different parts of the class hierarchy.
- **Detailed Explanation:** This design tightly binds classes and modules together, preventing reuse or modification without affecting other components.
- **Improvement Suggestions:** Pass state through constructors or via events rather than relying on shared global variables.
- **Priority Level:** High

---

### Code Smell Type: Blocking I/O Inside GUI Thread
- **Problem Location:** Use of `time.sleep(0.1)` inside `handle_click()`.
- **Detailed Explanation:** Blocking the GUI thread will freeze the interface for users, leading to poor UX. This practice should be avoided in any real-world Qt-based application.
- **Improvement Suggestions:** Replace blocking sleeps with asynchronous mechanisms such as `QTimer.singleShot()` or threading for non-blocking delays.
- **Priority Level:** High

---

### Code Smell Type: Lack of Documentation
- **Problem Location:** No docstrings or inline comments explaining functionality.
- **Detailed Explanation:** Without documentation, new developers struggle to grasp intent and usage patterns quickly. Especially important for UI-related logic.
- **Improvement Suggestions:** Add docstrings for public APIs and inline comments where logic isn’t immediately obvious.
- **Priority Level:** Low

---