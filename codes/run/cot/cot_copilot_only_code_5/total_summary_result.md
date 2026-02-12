## PR Total Summary

### Overall Conclusion
The PR introduces several functions to manage a global state, which is generally well-structured and functional. However, the code still suffers from some critical issues that block merging until addressed.

### Comprehensive Evaluation
- **Code Quality and Correctness**: 
  - The logic is mostly correct, but there is no explicit error handling, which could lead to runtime errors.
  - The use of global state makes the code harder to test and maintain.

- **Maintainability and Design Concerns**:
  - The code smells indicate issues with global state management, magic numbers, and long functions.
  - Lack of type hints and proper documentation further reduce maintainability.

- **Consistency with Existing Patterns or Standards**:
  - While the functions are named descriptively, the global state management pattern is unconventional and prone to issues.

### Final Decision Recommendation
**Request changes**

Justification:
- The code needs refactoring to avoid global state, add error handling, and improve modularity.
- Addressing these issues is crucial for maintaining clean and scalable code.

### Team Follow-Up
1. **Refactor Global State**: Encapsulate the global state in a class to improve encapsulation and make the code more testable.
2. **Add Error Handling**: Implement try-except blocks around critical sections to handle exceptions gracefully.
3. **Document Functions**: Provide clear docstrings for each function explaining their purpose and parameters.
4. **Type Hints**: Add type hints to improve code clarity and catch errors early.