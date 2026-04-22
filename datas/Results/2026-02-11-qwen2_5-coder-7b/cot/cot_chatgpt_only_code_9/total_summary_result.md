## PR Total Summary

### Overall Conclusion
- The PR does not meet merge criteria due to significant issues impacting readability, maintainability, and correctness.
- Blocking concerns include global state, magic numbers, duplicated code, tight coupling, and lack of error handling.

### Comprehensive Evaluation
- **Code Quality and Correctness**:
  - Issues identified include global state violations, magic numbers, and lack of proper error handling.
  - The use of direct print statements for output is discouraged.
- **Maintainability and Design Concerns**:
  - Functions are repetitive and tightly coupled to global state.
  - No separation of concerns between fetching and processing logic.
- **Consistency with Existing Patterns or Standards**:
  - Some naming conventions are consistent, but overall consistency is lacking.

### Final Decision Recommendation
- **Request changes**:
  - The PR requires substantial refactoring to address global state, error handling, and code organization.
  - Additional unit tests are essential to validate functionality.

### Team Follow-Up
- Refactor the code to eliminate global state and use dependency injection.
- Replace magic numbers with constants.
- Separate concerns between fetching and processing logic.
- Implement unit tests to cover various scenarios.