## Pull Request Summary

- **Key Changes**: Introduced a new module `bad_requests.py` containing a single function that performs multiple HTTP operations (GET and POST) using a global session and hardcoded URLs.
  
- **Impact Scope**: Affects only the newly added file `bad_requests.py`. No existing modules or dependencies are impacted directly.

- **Purpose of Changes**: Likely intended as a proof-of-concept or prototype for making HTTP requests; however, it does not follow best practices and is not production-ready.

- **Risks and Considerations**:
  - The use of global variables (`GLOBAL_SESSION`, `ANOTHER_GLOBAL`) can lead to unpredictable behavior and makes testing difficult.
  - Error handling is minimal and non-specific, potentially masking issues or leading to silent failures.
  - Function name and variable names are unclear and violate readability standards.
  - Hardcoded values reduce flexibility and make future maintenance harder.

- **Items to Confirm**:
  - Whether this is an intentional prototype or part of a larger refactor.
  - If this module will be integrated into any production workflow, proper refactoring is required before merging.
  - Consider replacing global state with dependency injection for better testability and maintainability.

---

## Code Review Feedback

### 1. **Readability & Consistency**
- ❌ **Issue**: Function name `functionThatDoesTooMuchAndIsHardToUnderstand()` violates naming conventions by being too long and not descriptive.
- ⚠️ **Issue**: Mixed language (Chinese/English) in comments and output messages reduces clarity for international teams.
- ✅ **Suggestion**: Rename function to something like `fetch_and_post_data()` and standardize message language.

### 2. **Naming Conventions**
- ❌ **Issue**: Use of `weirdVariableName` and `ANOTHER_GLOBAL` is unprofessional and breaks semantic clarity.
- ✅ **Suggestion**: Rename to `post_response` and `base_url`, respectively.

### 3. **Software Engineering Standards**
- ❌ **Issue**: Single function performing multiple responsibilities (HTTP calls, logging, error handling).
- ❌ **Issue**: Global state usage (`GLOBAL_SESSION`) introduces tight coupling and makes testing difficult.
- ✅ **Suggestion**: Break down logic into smaller, reusable functions and avoid global variables.

### 4. **Logic & Correctness**
- ❌ **Issue**: Broad exception handling (`except:` without specifying types) hides potential errors.
- ❌ **Issue**: No validation of HTTP responses beyond status code checks.
- ✅ **Suggestion**: Add specific exception handling and validate response content where applicable.

### 5. **Performance & Security**
- ❌ **Issue**: Using a global `Session` object may cause issues under concurrent loads or in multi-threaded environments.
- ⚠️ **Issue**: Hardcoded URLs and credentials increase risk of exposure in version control.
- ✅ **Suggestion**: Pass session and endpoints as parameters instead of globals; externalize sensitive data.

### 6. **Documentation & Testing**
- ❌ **Issue**: Missing docstrings or inline comments explaining purpose or expected inputs/outputs.
- ❌ **Issue**: No unit or integration tests provided.
- ✅ **Suggestion**: Add basic docstrings and include unit tests for each major operation.

### 7. **Scoring & Feedback Style**
- ✅ **Overall Score**: ⚠️ Needs Improvement
- 🔍 **Feedback Style**: Concise yet comprehensive, balancing brevity with clarity. Avoids over-engineering while addressing key concerns effectively.