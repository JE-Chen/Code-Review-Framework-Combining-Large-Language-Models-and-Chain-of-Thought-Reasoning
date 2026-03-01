
# Code Review Comment Evaluation Template

Please evaluate the review comments using the following scoring mechanism.  
Focus on whether the comments effectively help improve the code, especially by leveraging code smell and linter messages.

Score range: 1–100

Six evaluation dimensions:
1. Readability
    - 1–20: Comments are very hard to understand, poorly structured, confusing language.
    - 21–40: Some parts are readable, but many unclear sections remain.
    - 41–60: Comments are generally clear, but structure or phrasing needs improvement.
    - 61–80: Comments are well-structured, consistent, and easy to follow.
    - 81–100: Comments are highly readable, elegantly phrased, and well-organized.

2. Constructiveness (Maintainability)
    - 1–20: Comments lack constructive suggestions, no improvement direction.
    - 21–40: Comments provide partial suggestions, but vague or impractical.
    - 41–60: Comments offer basic improvement ideas, somewhat helpful.
    - 61–80: Comments are specific and actionable, clearly guiding improvements.
    - 81–100: Comments are highly constructive, offering clear and practical improvement paths.

3. Correctness
    - 1–20: Comments contain errors or misleading advice.
    - 21–40: Mostly correct, but important issues are overlooked.
    - 41–60: Largely correct, with only minor gaps.
    - 61–80: Correct and reasonable, with small room for refinement.
    - 81–100: Fully correct, logically sound, and precise in identifying issues.

4. Conciseness
    - 1–20: Comments are overly long, irrelevant to code improvement.
    - 21–40: Some relevant points, but too much unnecessary content.
    - 41–60: About half of the comments are focused and relevant.
    - 61–80: Most comments are concise and focused on improvement.
    - 81–100: All comments are precise, concise, and directly related to improvement.

5. Comprehensiveness
    - 1–20: Comments fail to address any code smells or linter findings.
    - 21–40: Comments mention at least one code smell or linter warning.
    - 41–60: Comments cover some code smells or linter findings.
    - 61–80: Comments cover most code smells and linter findings.
    - 81–100: Comments comprehensively address all code smells and linter findings, with improvement suggestions.

6. Relevance
    Relevance = (2 * Conciseness * Comprehensiveness) / (Conciseness + Comprehensiveness)

Reviewers should:
- Assign a score (1–100) for each dimension.
- Provide brief reasoning for each score.
- Conclude with an average score and overall recommendation.

## Review Comment:
First code review: 

### Code Review Summary

#### 1. **Readability & Consistency**
- **Indentation and Formatting**: Indentation is consistent and readable. Minor formatting improvements could be made for better alignment (e.g., aligning `GLOBAL_CACHE` declaration with other global constants).
- **Comments**: No inline comments are used, which reduces clarity where needed. Adding brief comments to explain complex logic or non-obvious behavior would improve understanding.

#### 2. **Naming Conventions**
- **Variables/Functions**: 
  - `get_users`, `get_posts`, and `get_todos` are clear but could benefit from more descriptive names like `fetch_users_data`, `fetch_posts_data`, etc., for consistency.
  - `process_all()` is vague; consider renaming to something like `run_data_processing` or `analyze_api_responses`.
  - `results` is okay as a variable name, but in loops, using more specific names like `user_result`, `post_result`, etc., can help readability.
- **Class Name**: `APIClient` is well-named and descriptive.

#### 3. **Software Engineering Standards**
- **Modularity & Duplication**:
  - The functions `get_users`, `get_posts`, and `get_todos` all follow a similar pattern and could be refactored into one generic function to reduce duplication.
  - Global state via `GLOBAL_CACHE` makes the code harder to reason about and test.
- **Maintainability**: 
  - Hardcoded endpoints (`/users`, `/posts`, `/todos`) make it difficult to extend or modify without changing multiple places.
  - There’s no error handling or retry mechanism for failed API calls.

#### 4. **Logic & Correctness**
- **Potential Bugs**:
  - If `response.status_code != 200`, an error dictionary is returned, but there's no logging or notification that an issue occurred — may hide real problems.
  - In `process_all()`, the filtering logic assumes all inputs have certain fields (`id`, `title`, `completed`). This may lead to runtime exceptions if those keys are missing.
  - Using `len(p.get("title", "")) > 15` might be fragile if title isn't always a string.

#### 5. **Performance & Security**
- **Performance**:
  - Repeatedly fetching data from the same client instance is fine, but caching in a global variable (`GLOBAL_CACHE`) introduces side effects and makes testing harder.
  - No rate limiting or caching strategies implemented beyond manual global cache usage.
- **Security**:
  - While not directly exposed, hardcoding URLs and headers in globals may become problematic in larger applications or when scaling.
  - Input validation is missing — particularly around user-provided data or API responses that aren’t strictly checked before use.

#### 6. **Documentation & Testing**
- **Documentation**:
  - Minimal inline documentation. Consider adding docstrings to functions for clarity.
  - Missing type hints or annotations for better IDE support and maintainability.
- **Testing**:
  - No unit tests or mocking examples provided.
  - Difficult to write unit tests due to reliance on global state (`GLOBAL_CACHE`) and external HTTP calls.

#### 7. **Improvement Suggestions**
- Refactor repeated logic in `get_users`, `get_posts`, and `get_todos` into a single helper method.
- Replace `GLOBAL_CACHE` with local or scoped caching (e.g., per session or request context).
- Add defensive checks for missing keys in dictionaries during processing (e.g., `u.get("id")`).
- Improve control flow in `main()` by simplifying nested conditionals.
- Use logging instead of silent error returns in `fetch()` method.
- Add docstrings and type hints for improved clarity and maintainability.
- Consider making `BASE_URL` configurable rather than hardcoded.

---

This review focuses on key structural and logical concerns while maintaining brevity and actionable feedback.

First summary: 

### Pull Request Summary

- **Key Changes**  
  - Introduced `APIClient` class for making HTTP requests to a REST API.
  - Added functions (`get_users`, `get_posts`, `get_todos`) to fetch and cache data from endpoints.
  - Implemented `process_all()` to analyze fetched data and generate filtered results.
  - Added `main()` function to run the workflow and display output with dynamic messages based on result count.

- **Impact Scope**  
  - Affects the entire module as it defines core logic for fetching, caching, and processing external API data.
  - Uses a global cache (`GLOBAL_CACHE`) which may cause issues in multi-threaded environments or when used in larger systems.

- **Purpose of Changes**  
  - Adds basic functionality to interact with a public JSONPlaceholder API.
  - Demonstrates how to structure an API client and perform simple data processing logic.

- **Risks and Considerations**  
  - Global state via `GLOBAL_CACHE` can lead to concurrency issues and makes testing harder.
  - No error handling for invalid inputs or malformed responses beyond basic HTTP checks.
  - The conditional logic in `main()` could be simplified using a switch-like pattern or mapping.

- **Items to Confirm**  
  - Ensure thread safety if this code will run in concurrent contexts.
  - Validate whether caching behavior is intentional and safe for all use cases.
  - Confirm that no additional validation or sanitization is needed for fetched data before processing.

---

## Code Review

### 1. Readability & Consistency
- ✅ Indentation and formatting are consistent.
- ⚠️ Comments are minimal; consider adding docstrings for classes and functions for better clarity.
- 🧼 Minor formatting improvements like spacing around operators would enhance readability slightly.

### 2. Naming Conventions
- ✅ Function and variable names are descriptive (`fetch`, `get_users`, `process_all`).
- ⚠️ `GLOBAL_CACHE` uses uppercase but doesn't follow typical naming convention for constants (should ideally be `global_cache` or similar).
- 🔁 Class name `APIClient` is appropriate and clear.

### 3. Software Engineering Standards
- ❌ **Global State**: Use of `GLOBAL_CACHE` introduces tight coupling and reduces modularity. This makes the code hard to test and maintain.
- 🔄 **Duplication**: Functions `get_users`, `get_posts`, and `get_todos` have nearly identical logic — they can be refactored into one generic method.
- 🧪 Missing unit tests for any part of the logic — critical for ensuring correctness and preventing regressions.

### 4. Logic & Correctness
- ✅ Basic logic seems correct for fetching data and filtering results.
- ⚠️ Error handling is limited to returning error dictionaries — does not handle malformed JSON or unexpected response structures gracefully.
- ⚠️ Conditional checks like `if u.get("id") == 1:` assume a specific ID value, which might not always be reliable without validation.

### 5. Performance & Security
- ⚠️ Global session usage (`SESSION`) is okay for single-threaded usage but could introduce race conditions in async or threaded applications.
- 🔐 Input validation is missing — raw JSON data from an external source should be validated before use.

### 6. Documentation & Testing
- 📝 Docstrings are absent from functions and classes — adding them improves discoverability and maintainability.
- 🧪 No unit tests provided — especially important for network-dependent and logic-heavy code.

### 7. Final Notes
This code provides a working prototype for interacting with an API and analyzing its data. However, due to global state and lack of abstraction, it's not production-ready. Refactoring to remove global dependencies and adding tests would significantly improve quality.

#### Suggested Improvements:
- Replace `GLOBAL_CACHE` with local or injectable caching mechanism.
- Refactor repeated logic into a common helper function.
- Add docstrings and basic type hints.
- Implement unit tests for core logic and edge cases.
- Consider asynchronous support if scalability becomes an issue.

---

Total summary: 

 ### 1. **Overall Conclusion**

The PR introduces basic API interaction and data processing logic but fails to meet merge criteria due to **critical design flaws** and **low maintainability**. Key concerns include:
- **Blocking Issues**: Use of global state (`GLOBAL_CACHE`) and lack of dependency injection make the code non-testable and unsafe for concurrent use.
- **High-Priority Code Smells**: Duplicate functions, broad exception handling, and magic strings significantly reduce modularity and clarity.
- **Missing Testing & Documentation**: No unit tests or docstrings are present, reducing confidence in correctness and future maintainability.

Non-blocking improvements (e.g., minor formatting) are noted but do not outweigh the architectural weaknesses.

---

### 2. **Comprehensive Evaluation**

#### **Code Quality & Correctness**
- Functions `get_users`, `get_posts`, and `get_todos` are functionally equivalent and duplicated—violating DRY principles.
- Error handling is overly broad (`except Exception`) and silently returns error dicts without logging or raising exceptions.
- Filtering logic in `process_all()` assumes presence of specific keys (`id`, `title`, `completed`) without validation, risking runtime errors.
- Magic numbers and hardcoded strings (e.g., `"Long Post:"`, `5`, `20`) reduce flexibility and increase maintenance cost.

#### **Maintainability & Design Concerns**
- **Global State Dependency**: `GLOBAL_CACHE` introduces tight coupling and side effects, making the code hard to test and reuse.
- **Tight Coupling**: The `APIClient` is instantiated directly in `process_all()` and relies on a global session, violating separation of concerns.
- **Lack of Abstraction**: Repeated logic and shared responsibilities suggest opportunities for refactoring into a more modular structure.

#### **Consistency with Standards**
- No consistent naming or formatting conventions (e.g., uppercase for `GLOBAL_CACHE` vs. lowercase variables).
- Absence of docstrings, type hints, and inline comments makes it difficult to understand intent or behavior.
- Hardcoded endpoints and message strings violate configurability best practices.

---

### 3. **Final Decision Recommendation**

**Request Changes**

This PR should not be merged until critical structural and design issues are addressed:
- Refactor duplicate API-fetching functions into a generic helper.
- Remove reliance on `GLOBAL_CACHE` and replace with injectable or local caching.
- Improve exception handling to catch specific errors.
- Add docstrings and type hints for clarity.
- Simplify nested conditionals in `main()`.

These changes are essential for improving **testability**, **modularity**, and **long-term sustainability** of the codebase.

---

### 4. **Team Follow-Up**

- **Refactor Core Logic**: Implement a generic `fetch_endpoint` function to eliminate duplication.
- **Replace Global Cache**: Introduce a caching layer tied to `APIClient` instances or a scoped context.
- **Enhance Error Handling**: Replace broad `except Exception` with targeted exception types.
- **Add Unit Tests**: Begin writing tests for `APIClient`, `process_all`, and edge cases.
- **Document Code**: Add docstrings to all functions and classes, along with type hints for parameters and return values.
- **Review Conditional Flow**: Restructure nested `if/elif/else` blocks in `main()` for improved readability.

Step by step analysis: 

### 1. **No Global Variables (`no-global-variables`)**
- **Issue**: The global variable `GLOBAL_CACHE` reduces modularity and testability.
- **Explanation**: Using a global cache makes the functions dependent on shared state, which complicates unit testing and makes it hard to reason about code behavior.
- **Why It Happens**: Global variables introduce tight coupling between components.
- **Impact**: Makes code harder to test, debug, and reuse in different contexts.
- **Fix**: Pass cache as a parameter or encapsulate caching logic in a class.
  ```python
  def get_users(client, cache=None):
      if cache is None:
          cache = {}
      ...
  ```

---

### 2. **Unused Variable (`no-unused-vars`)**
- **Issue**: Variable `r` in the main loop is unused.
- **Explanation**: The variable `r` is only used for printing but never actually processed or returned.
- **Why It Happens**: Likely leftover from debugging or copy-paste.
- **Impact**: Confusing for readers; reduces code clarity.
- **Fix**: Remove unused variable or refactor to use it meaningfully.
  ```python
  # Before
  for r in results:
      print(r)

  # After
  for item in results:
      print(item)
  ```

---

### 3. **Duplicate Code (`no-duplicate-code`)**
- **Issue**: Functions `get_users`, `get_posts`, and `get_todos` have nearly identical logic.
- **Explanation**: Each function performs the same steps—fetch data, update cache, return results.
- **Why It Happens**: Lack of abstraction leads to repetition.
- **Impact**: Difficult to maintain and extend when logic needs updating.
- **Fix**: Extract common logic into a generic function.
  ```python
  def fetch_endpoint(client, endpoint, cache):
      if endpoint in cache:
          return cache[endpoint]
      response = client.fetch(endpoint)
      cache[endpoint] = response
      return response
  ```

---

### 4. **Implicit Exception Handling (`no-implicit-exception-handling`)**
- **Issue**: Catches all exceptions (`except Exception as e:`).
- **Explanation**: This catches everything including system-level errors, masking real bugs.
- **Why It Happens**: Lazy error handling due to lack of specificity.
- **Impact**: Makes debugging harder and can hide critical runtime issues.
- **Fix**: Catch specific exceptions like `requests.RequestException`.
  ```python
  except requests.RequestException as e:
      print(f"Request failed: {e}")
  ```

---

### 5. **Hardcoded Values (`no-hardcoded-values`)**
- **Issue**: Hardcoded strings like `'Special User:'` and `'Long Post:'`.
- **Explanation**: These literals should be constants to avoid duplication and improve consistency.
- **Why It Happens**: Direct use of magic strings without abstraction.
- **Impact**: Maintenance overhead; changes require updates in multiple locations.
- **Fix**: Define them as module-level constants.
  ```python
  SPECIAL_USER_PREFIX = "Special User:"
  LONG_POST_PREFIX = "Long Post:"
  ```

---

### 6. **Magic Numbers (`no-magic-numbers`)**
- **Issue**: Magic numbers `5` and `20` appear directly in logic.
- **Explanation**: Unnamed numeric thresholds reduce readability and flexibility.
- **Why It Happens**: Numeric literals used without context.
- **Impact**: Difficult to understand intent and modify later.
- **Fix**: Replace with named constants.
  ```python
  MIN_RESULTS_THRESHOLD = 5
  MAX_RESULTS_THRESHOLD = 20
  ```

---

### 7. **Side Effects in Functions (`no-side-effects-in-functions`)**
- **Issue**: Functions modify `GLOBAL_CACHE`, creating side effects.
- **Explanation**: Side effects make functions unpredictable and harder to test.
- **Why It Happens**: Not following functional principles—functions shouldn’t alter external state.
- **Impact**: Leads to brittle code and race conditions.
- **Fix**: Return data and let caller manage caching.
  ```python
  def get_users(client):
      response = client.fetch("/users")
      return response  # No modification of cache here
  ```

---

### 8. **Unneeded Else Block (`no-unneeded-else`)**
- **Issue**: Nested if/else blocks reduce readability.
- **Explanation**: Complex nesting can obscure control flow.
- **Why It Happens**: Poor structuring of conditional logic.
- **Impact**: Harder to read and maintain.
- **Fix**: Simplify with early returns or `elif`.
  ```python
  # Before
  if count > 5:
      if count < 20:
          print("Medium")
      else:
          print("High")
  else:
      print("Low")

  # After
  if count <= 5:
      print("Low")
  elif count <= 20:
      print("Medium")
  else:
      print("High")
  ```

---

## Code Smells:
## Code Review Summary

The provided Python script implements a basic API client and processing logic for fetching and analyzing data from `jsonplaceholder.typicode.com`. While functional, several **code smells** and anti-patterns are present that affect **readability**, **maintainability**, and **scalability**. Below is a structured analysis.

---

## Code Smell 1: Global State Usage (Global Cache)
- **Code Smell Type:** Global State Dependency
- **Problem Location:** `GLOBAL_CACHE = {}` and usage in `get_users`, `get_posts`, `get_todos`
- **Detailed Explanation:** Using a global variable (`GLOBAL_CACHE`) introduces tight coupling and makes testing difficult. It also complicates concurrent execution or reuse in different contexts because it's not isolated per instance or request.
- **Improvement Suggestions:** Replace with an instance-level cache inside `APIClient`, or pass a caching mechanism as a dependency. Alternatively, implement proper caching strategies using external libraries like `functools.lru_cache`.
- **Priority Level:** High

---

## Code Smell 2: Duplicate Code in Fetch Functions
- **Code Smell Type:** Code Duplication
- **Problem Location:** `get_users`, `get_posts`, `get_todos` functions
- **Detailed Explanation:** All three functions perform nearly identical operations: fetch data via `client.fetch()`, store in `GLOBAL_CACHE`, and return. This violates DRY (Don't Repeat Yourself) and increases maintenance overhead.
- **Improvement Suggestions:** Refactor into a generic helper function or use a parameterized approach such as `fetch_endpoint(endpoint)` that handles common logic.
- **Priority Level:** High

---

## Code Smell 3: Magic Strings / Hardcoded Values
- **Code Smell Type:** Magic Strings
- **Problem Location:** String literals `"users"`, `"posts"`, `"todos"` used as keys in `GLOBAL_CACHE`; hardcoded string comparisons in `process_all()`
- **Detailed Explanation:** These values lack semantic meaning and make future changes harder. If these endpoints change, they must be updated in multiple places.
- **Improvement Suggestions:** Define constants for endpoint paths and cache keys. For example:
  ```python
  USERS_ENDPOINT = "/users"
  POSTS_ENDPOINT = "/posts"
  TODOS_ENDPOINT = "/todos"
  ```
- **Priority Level:** Medium

---

## Code Smell 4: Inconsistent Naming and Lack of Type Hints
- **Code Smell Type:** Poor Naming Conventions
- **Problem Location:** Variables like `u`, `p`, `t` in loops within `process_all()`; missing type hints
- **Detailed Explanation:** Non-descriptive variable names reduce readability and understanding. Adding type hints improves code clarity and helps catch errors early.
- **Improvement Suggestions:** Use descriptive variable names like `user`, `post`, `todo`. Add typing hints for parameters and return types.
- **Priority Level:** Medium

---

## Code Smell 5: Nested Conditional Logic
- **Problem Location:** Conditional blocks in `main()` function regarding result counts
- **Detailed Explanation:** The nested conditional structure (`if ... elif ... else`) reduces readability and can be simplified using a mapping or switch-like behavior.
- **Improvement Suggestions:** Replace nested conditionals with a cleaner control flow or a dictionary-based lookup.
- **Priority Level:** Medium

---

## Code Smell 6: Exception Handling Is Too Broad
- **Code Smell Type:** Overly Broad Exception Handling
- **Problem Location:** `except Exception as e:` in `APIClient.fetch()`
- **Detailed Explanation:** Catching all exceptions without differentiation prevents debugging and masking actual issues. It could hide network failures, invalid responses, or unexpected behavior.
- **Improvement Suggestions:** Catch specific exceptions like `requests.exceptions.RequestException` or handle known error cases explicitly.
- **Priority Level:** High

---

## Code Smell 7: Tight Coupling Between Components
- **Code Smell Type:** Tight Coupling
- **Problem Location:** Direct instantiation of `APIClient` in `process_all()`; reliance on global session
- **Detailed Explanation:** The code tightly couples components, making it hard to swap dependencies or test independently. A better design would allow injection of dependencies.
- **Improvement Suggestions:** Pass `APIClient` instance as a parameter or inject dependencies through constructors or factories.
- **Priority Level:** Medium

---

## Code Smell 8: Lack of Input Validation and Error Propagation
- **Code Smell Type:** Insufficient Input Validation / Error Propagation
- **Problem Location:** `fetch()` method and related functions
- **Detailed Explanation:** There's no validation of input parameters (e.g., endpoint path). Also, the error handling just returns a dict with error messages — but doesn’t raise or propagate meaningful exceptions.
- **Improvement Suggestions:** Validate inputs, log errors appropriately, and consider raising custom exceptions for better error propagation.
- **Priority Level:** Medium

---

## Code Smell 9: Inefficient Logic in Loop Conditions
- **Problem Location:** Loop conditions in `process_all()`
- **Detailed Explanation:** Multiple loops over collections with similar filtering logic can be optimized by combining them or using list comprehensions or generator expressions where applicable.
- **Improvement Suggestions:** Combine filtering logic into one pass or refactor to use more efficient iteration patterns.
- **Priority Level:** Low

---

## Code Smell 10: Missing Documentation and Docstrings
- **Code Smell Type:** Poor Documentation
- **Problem Location:** All functions lack docstrings or inline comments
- **Detailed Explanation:** Without documentation, it’s hard to understand the purpose of functions and how they interact, especially for new developers or during maintenance.
- **Improvement Suggestions:** Add docstrings explaining what each function does, its parameters, and return values. Include inline comments for complex logic.
- **Priority Level:** Medium

---

## Summary Table

| Code Smell Type              | Priority |
|-----------------------------|----------|
| Global State Usage          | High     |
| Code Duplication            | High     |
| Magic Strings               | Medium   |
| Poor Naming                 | Medium   |
| Nested Conditionals         | Medium   |
| Broad Exception Handling    | High     |
| Tight Coupling              | Medium   |
| Insufficient Input Validation | Medium |
| Inefficient Loop Logic      | Low      |
| Missing Documentation       | Medium   |

---

## Recommendations Recap

1. **Refactor duplicate functions** into a reusable utility.
2. **Replace global state** with local or injected caches.
3. **Use constants** for endpoint strings and cache keys.
4. **Improve naming conventions** for clarity.
5. **Avoid broad exception catching**; use specific ones.
6. **Inject dependencies** instead of relying on globals.
7. **Add docstrings and type hints** for better maintainability.
8. **Simplify conditional structures** for readability.
9. **Consider performance improvements** in loop logic.

By addressing these issues, the code will become more modular, readable, and robust.

## Linter Messages:
```json
[
  {
    "rule_id": "no-global-variables",
    "severity": "warning",
    "message": "Usage of global variable 'GLOBAL_CACHE' reduces modularity and testability.",
    "line": 8,
    "suggestion": "Pass cache as a parameter or use a class-based approach to encapsulate state."
  },
  {
    "rule_id": "no-unused-vars",
    "severity": "warning",
    "message": "Variable 'r' in the main loop is unused; it's only used for printing.",
    "line": 48,
    "suggestion": "Remove unused variable or refactor to use it meaningfully."
  },
  {
    "rule_id": "no-duplicate-code",
    "severity": "warning",
    "message": "Functions 'get_users', 'get_posts', and 'get_todos' have nearly identical logic and can be refactored into one generic function.",
    "line": 21,
    "suggestion": "Create a single reusable function that accepts an endpoint and handles caching."
  },
  {
    "rule_id": "no-implicit-exception-handling",
    "severity": "warning",
    "message": "Catching all exceptions without specifying types may mask unexpected errors.",
    "line": 16,
    "suggestion": "Catch specific exceptions such as requests.RequestException or ValueError."
  },
  {
    "rule_id": "no-hardcoded-values",
    "severity": "warning",
    "message": "Hardcoded strings like 'Special User:', 'Long Post:', etc., should be extracted to constants or configuration.",
    "line": 37,
    "suggestion": "Define these string literals as constants at module level for consistency and maintainability."
  },
  {
    "rule_id": "no-magic-numbers",
    "severity": "warning",
    "message": "Magic numbers 5 and 20 are used directly in conditional logic; consider extracting them into named constants.",
    "line": 51,
    "suggestion": "Replace magic numbers with named constants (e.g., MIN_RESULTS_THRESHOLD, MAX_RESULTS_THRESHOLD)."
  },
  {
    "rule_id": "no-side-effects-in-functions",
    "severity": "warning",
    "message": "Function 'get_users', 'get_posts', and 'get_todos' modify the global cache, which creates side effects.",
    "line": 21,
    "suggestion": "Avoid modifying external state from functions; instead, return data and let calling code handle caching."
  },
  {
    "rule_id": "no-unneeded-else",
    "severity": "warning",
    "message": "Nested if statements can be simplified by restructuring logic.",
    "line": 53,
    "suggestion": "Simplify nested conditionals using elif or early returns to improve readability."
  }
]
```

## Origin code



