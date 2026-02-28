## Code Smell Analysis

### 1. Code Smell Type: Global State Dependency
- **Problem Location:** `GLOBAL_CACHE` variable and its usage in `get_users`, `get_posts`, `get_todos`
- **Detailed Explanation:** The use of a global cache (`GLOBAL_CACHE`) introduces tight coupling between functions and makes the system non-deterministic. This violates the principle of stateless operations and makes testing difficult since function behavior depends on external mutable state. Additionally, it's not thread-safe and can lead to race conditions in concurrent environments.
- **Improvement Suggestions:** Replace the global cache with an instance-based caching mechanism within the `APIClient` class. Alternatively, pass the cache as a parameter or implement a proper caching layer with appropriate locking mechanisms if concurrency is required.
- **Priority Level:** High

### 2. Code Smell Type: Duplicate Code
- **Problem Location:** `get_users`, `get_posts`, `get_todos` functions
- **Detailed Explanation:** These three functions exhibit identical logic patterns—fetching data from an endpoint, storing it in the global cache, and returning it. This duplication violates DRY (Don't Repeat Yourself) principles and increases maintenance burden when changes are needed.
- **Improvement Suggestions:** Refactor these into a single generic function that accepts endpoint parameters and handles caching internally. For example: `def fetch_endpoint(client, endpoint, cache_key=None):`.
- **Priority Level:** High

### 3. Code Smell Type: Magic Numbers/Strings
- **Problem Location:** `"users"`, `"posts"`, `"todos"` string literals in `GLOBAL_CACHE` assignments
- **Detailed Explanation:** Using hardcoded strings as keys in the global cache reduces maintainability and readability. If these values change or become inconsistent, they're hard to track down. It also makes the code less flexible and harder to extend.
- **Improvement Suggestions:** Define constants for these keys at module level or use an enum structure to manage them consistently.
- **Priority Level:** Medium

### 4. Code Smell Type: Inconsistent Error Handling
- **Problem Location:** Exception handling in `APIClient.fetch()` method
- **Detailed Explanation:** While there is basic exception handling, it returns generic error messages without logging or distinguishing between different types of exceptions. This makes debugging harder and doesn't provide enough information for callers to handle errors appropriately.
- **Improvement Suggestions:** Log exceptions before returning them, differentiate between network errors, HTTP errors, and other exceptions, and consider raising custom exceptions instead of returning dictionaries with error fields.
- **Priority Level:** Medium

### 5. Code Smell Type: Violation of Single Responsibility Principle
- **Problem Location:** `process_all()` function
- **Detailed Explanation:** The `process_all()` function does more than one thing—it orchestrates API calls, processes data, and applies business logic. This makes it hard to test in isolation and understand the flow of execution. Each responsibility (data fetching, data processing, result generation) should ideally be separated.
- **Priority Level:** Medium

### 6. Code Smell Type: Hardcoded Conditions
- **Problem Location:** Logic inside loops in `process_all()`
- **Detailed Explanation:** The conditions like checking `u.get("id") == 1` or `len(p.get("title", "")) > 15` are hardcoded business rules embedded directly in the code. These should be extracted into configurable constants or moved to dedicated handler functions to improve maintainability and flexibility.
- **Priority Level:** Medium

### 7. Code Smell Type: Inefficient Conditional Structure
- **Problem Location:** Nested conditional blocks in `main()` function
- **Detailed Explanation:** The nested `if-else` statements for determining result counts create a complex control flow that could be simplified using elif chains or a mapping approach. This affects readability and can make future modifications error-prone.
- **Priority Level:** Low

### 8. Code Smell Type: Lack of Input Validation
- **Problem Location:** All functions lack explicit input validation
- **Detailed Explanation:** There’s no validation for inputs such as URLs, endpoints, or expected response structures. If any part of the request fails or returns unexpected data, the application might crash or behave unpredictably.
- **Priority Level:** Medium

### 9. Code Smell Type: Poor Code Organization
- **Problem Location:** Mixing of API interaction, data processing, and presentation logic
- **Detailed Explanation:** The code mixes concerns by placing API client logic, business rule processing, and user-facing output in the same file and functions. A better architecture would separate these concerns into modules or classes.
- **Priority Level:** Medium

### 10. Code Smell Type: Suboptimal Naming
- **Problem Location:** Function names like `get_users`, `get_posts`, `get_todos`
- **Detailed Explanation:** While these names are somewhat descriptive, they don’t clearly indicate their purpose beyond just fetching data. More descriptive names that reflect what they do (e.g., `fetch_and_cache_users`) would improve clarity.
- **Priority Level:** Low