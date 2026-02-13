## PR Total Summary

### Overall Conclusion
The PR introduces some functional enhancements but suffers from several issues that affect its readability, maintainability, and overall quality. While the division of tasks and addition of functions are positive steps, the code lacks cohesion, clarity, and robustness. Therefore, the PR does **not** meet the merge criteria at this time.

### Comprehensive Evaluation
- **Code Quality and Correctness**:
  - The code introduces minor logical errors (division by zero in `calculate_average_scores`) and missing input validations.
  - It also lacks extensive documentation and unit tests, leaving gaps in understanding and verification.

- **Maintainability and Design Concerns**:
  - The code smells identified (long functions, magic numbers, inefficient data access) severely impact the maintainability and scalability of the code.
  - The `main` function mixes concerns, making it hard to read and understand.

- **Consistency with Existing Patterns or Standards**:
  - The code diverges significantly from the existing pattern of modular, testable functions, leading to inconsistency.

### Final Decision Recommendation
**Request changes**:
- Address the long functions by breaking them down into smaller, focused functions.
- Replace magic numbers with named constants.
- Implement input validation and handle edge cases.
- Add comprehensive documentation and unit tests.
- Refactor the `main` function to separate concerns.

### Team Follow-Up
- Conduct a code review meeting to discuss the identified issues and proposed solutions.
- Establish a coding standard guideline for consistent naming and structuring.
- Ensure all future contributions undergo similar thorough reviews.