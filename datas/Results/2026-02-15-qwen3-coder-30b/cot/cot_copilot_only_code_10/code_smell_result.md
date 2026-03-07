### Code Smell Type: Global State Dependency
- **Problem Location:** `GLOBAL_CACHE` usage in `get_users`, `get_posts`, `get_todos`
- **Detailed Explanation:** Using a global variable (`GLOBAL_CACHE`) introduces hidden dependencies and makes the system non-deterministic. It's difficult to reason about state changes or reproduce behavior since external state affects function outputs.
- **Improvement Suggestions:** Replace with local caching or inject cache as dependency into `APIClient`.
- **Priority Level:** High

---

### Code Smell Type: Duplicated Code
- **Problem Location:** Similar logic inside `get_users`, `get_posts`, `get_todos`
- **Detailed Explanation:** The three functions perform nearly identical operations—fetching from an endpoint, storing in cache, returning data. This violates DRY (Don't Repeat Yourself), making future changes harder and increasing risk of inconsistencies.
- **Improvement Suggestions:** Extract common logic into a reusable method like `fetch_and_cache(endpoint)` within `APIClient`.
- **Priority Level:** High

---

### Code Smell Type: Magic Numbers
- **Problem Location:** Thresholds in conditional checks (`len(title) > 15`, result count thresholds)
- **Detailed Explanation:** Hardcoded values reduce readability and make adjustments brittle. These numbers should have descriptive names or constants to clarify intent.
- **Improvement Suggestions:** Define constants for thresholds such as `MAX_TITLE_LENGTH = 15`, `FEW_RESULTS_THRESHOLD = 5`, etc.
- **Priority Level:** Medium

---

### Code Smell Type: Poor Error Handling
- **Problem Location:** Generic exception handling in `fetch()` method
- **Detailed Explanation:** Catch-all exceptions mask underlying issues and prevent proper error propagation. Specific errors should be handled differently to improve debugging and resilience.
- **Priority Level:** Medium

---

### Code Smell Type: Tight Coupling
- **Problem Location:** Direct instantiation of `APIClient` in `process_all()`
- **Detailed Explanation:** The `process_all()` function tightly couples to concrete implementation details, reducing flexibility and testability. Dependency injection would allow easier mocking and reuse.
- **Improvement Suggestions:** Accept `APIClient` instance as parameter or use dependency injection container.
- **Priority Level:** Medium

---

### Code Smell Type: Lack of Input Validation
- **Problem Location:** No validation on user-provided inputs (URLs, data structures)
- **Detailed Explanation:** Missing input sanitization opens up potential vulnerabilities, especially when dealing with external APIs or user-generated content.
- **Improvement Suggestions:** Validate endpoint paths and ensure expected fields exist before processing.
- **Priority Level:** Medium

---

### Code Smell Type: Inconsistent Naming
- **Problem Location:** Mixed naming styles between snake_case (`get_users`) and camelCase (`process_all`)
- **Detailed Explanation:** Inconsistent naming reduces code consistency and makes it harder to understand structure at a glance.
- **Improvement Suggestions:** Adopt one standard (preferably snake_case per PEP8) and apply uniformly.
- **Priority Level:** Low

---

### Code Smell Type: Unnecessary Complexity in Conditional Logic
- **Problem Location:** Nested conditionals in `main()` for result counts
- **Detailed Explanation:** Overly nested `if-else` blocks complicate understanding and increase cyclomatic complexity. Simplifying these conditions improves readability.
- **Improvement Suggestions:** Use early returns or switch-case patterns where appropriate.
- **Priority Level:** Low

---

### Code Smell Type: Lack of Documentation
- **Problem Location:** Missing docstrings or inline comments
- **Detailed Explanation:** Without clear documentation, other developers struggle to grasp purpose and expected behavior quickly.
- **Improvement Suggestions:** Add docstrings explaining each public API component and key logic decisions.
- **Priority Level:** Low

---

### Code Smell Type: Single Responsibility Principle Violation
- **Problem Location:** `process_all()` combines data fetching and business logic
- **Detailed Explanation:** The function performs multiple unrelated tasks—data retrieval, caching, filtering, and reporting—which reduces modularity and testability.
- **Improvement Suggestions:** Separate concerns by extracting data processing logic into dedicated modules or classes.
- **Priority Level:** Medium