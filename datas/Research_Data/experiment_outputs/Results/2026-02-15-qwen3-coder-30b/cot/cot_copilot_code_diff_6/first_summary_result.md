### 📌 **Pull Request Summary**

- **Key Changes**  
  Introduces a new module `bad_requests.py` containing a single function that performs multiple HTTP operations without clear separation or error handling best practices.

- **Impact Scope**  
  Affects only the newly added file `bad_requests.py`. No existing modules impacted directly.

- **Purpose of Changes**  
  Likely an initial prototype or proof-of-concept demonstrating raw API interaction, but lacks structure and robustness for production use.

- **Risks and Considerations**  
  - Function does too much; violates single-responsibility principle.
  - Global state usage increases risk of side effects.
  - Broad exception handling hides real issues.
  - Hardcoded URLs reduce flexibility and testability.

- **Items to Confirm**  
  - Whether this is meant as a temporary PoC or will evolve into a proper service client.
  - If any tests or logging strategy exists beyond `print()` statements.
  - Whether `GLOBAL_SESSION` is intended to be reused safely in concurrent environments.

---

### ✅ **Code Review Feedback**

#### 1. **Readability & Consistency**
- ❌ Poor formatting and inconsistent naming (`weirdVariableName`, `ANOTHER_GLOBAL`) make code hard to read.
- ⚠️ Mixing English and Chinese comments reduces professionalism.
- ✅ Use consistent naming, spacing, and comments aligned with team style guides.

#### 2. **Naming Conventions**
- ❌ Function name `functionThatDoesTooMuchAndIsHardToUnderstand()` is verbose and unidiomatic.
- ❌ Variables like `weirdVariableName` do not reflect their purpose.
- ✅ Prefer descriptive names such as `fetch_post_data()` or `send_api_request()`.

#### 3. **Software Engineering Standards**
- ❌ Violates SRP — one function handles fetching, printing, and post-processing.
- ❌ Global variables (`GLOBAL_SESSION`, `ANOTHER_GLOBAL`) introduce hidden dependencies.
- ⚠️ No modularity or encapsulation — hard to reuse or extend.
- ✅ Refactor into smaller, reusable functions or classes.

#### 4. **Logic & Correctness**
- ❌ Broad `except:` blocks mask actual errors (e.g., network failures).
- ❌ Lack of status checks or validation leads to silent failures.
- ⚠️ Hardcoded paths increase brittleness.
- ✅ Add explicit error checking and structured responses.

#### 5. **Performance & Security**
- ❌ Reusing session unnecessarily may cause issues under load.
- ⚠️ No timeout configured for requests — could hang indefinitely.
- ❌ Unvalidated inputs used in POST body (though example data here).
- ✅ Set timeouts and validate payloads where applicable.

#### 6. **Documentation & Testing**
- ❌ No docstrings or inline comments explaining behavior.
- ❌ No unit tests exist to verify functionality.
- ✅ Include docstrings and consider adding mock-based tests.

#### 7. **Scoring & Feedback Style**
- Score: ⭐⭐☆☆☆ (Low) – Needs significant rework.
- Suggestion: Rewrite using dependency injection, structured logging, and modular design.

---

### 💡 **Recommendations**
1. Split responsibilities into dedicated helper functions.
2. Replace global session with local instance or injectable client.
3. Improve error handling and logging.
4. Add parameterization for endpoints and data.
5. Integrate with standard testing framework (pytest, unittest).