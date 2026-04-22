### Overall Conclusion
- **Blocking Concerns**: Significant code smells and potential bugs that require addressing before merging.
- **Non-Blocking Concerns**: Some minor stylistic issues and missing documentation.

### Comprehensive Evaluation
- **Code Quality and Correctness**:
  - Several logical errors and redundant calculations identified.
  - Lack of proper testing and documentation.
  
- **Maintainability and Design Concerns**:
  - Tightly coupled functions and global state.
  - Presence of magic numbers and unnecessary complexity.

- **Consistency with Existing Patterns or Standards**:
  - No explicit deviations from team conventions noted.

### Final Decision Recommendation
**Request Changes**

**Justification**:
- Critical issues such as redundant calculations and inconsistent naming conventions must be addressed to ensure code quality.
- The presence of global variables and lack of proper testing hinder maintenance and scalability.
- Adequate documentation and refactoring are necessary to improve code readability and reliability.

### Team Follow-Up
1. **Address Redundant Calculations**: Extract common calculations into separate functions.
2. **Refactor Functions**: Break down `calcStats` and other functions into smaller, focused functions.
3. **Replace Magic Numbers**: Define constants for significant values with explanatory names.
4. **Improve Documentation**: Add docstrings and comments to explain function purposes and parameters.
5. **Unit Testing**: Write unit tests for individual functions to ensure correctness.