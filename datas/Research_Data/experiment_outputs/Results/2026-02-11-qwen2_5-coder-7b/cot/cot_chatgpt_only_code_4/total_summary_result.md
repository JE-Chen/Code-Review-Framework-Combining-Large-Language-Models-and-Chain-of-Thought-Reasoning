## PR Total Summary

### Overall Conclusion
The PR partially meets merge criteria, but several critical issues need addressing. Specifically, significant refactoring and additional testing are required to ensure robustness and maintainability.

### Comprehensive Evaluation
1. **Code Quality and Correctness**
   - **Positive**: The code generally works as intended, but it lacks proper error handling and boundary condition checks.
   - **Negative**: Long methods and duplicated logic reduce readability and maintainability. Lack of comprehensive unit tests and insufficient documentation hinder future development.

2. **Maintainability and Design Concerns**
   - **Positive**: Classes are mostly modular, but there is a lack of separation of concerns, particularly between formatting and exporting logic.
   - **Negative**: Global configuration and tight coupling increase complexity and maintenance overhead. Magic numbers and lack of comments complicate understanding.

3. **Consistency with Existing Patterns or Standards**
   - **Positive**: Adheres to Python naming conventions and basic principles of object-oriented design.
   - **Negative**: Inconsistent application of SOLID principles, such as SRP and DRY.

### Final Decision Recommendation
**Request changes**

Justification:
- Significant improvements are needed in terms of code organization, error handling, and testing.
- Current implementation lacks essential features like robust error handling and proper separation of concerns.
- Additional documentation and unit tests are crucial to ensure reliability and ease of maintenance.

### Team Follow-Up
1. **Refactor `ReportService` and `ExportManager`**:
   - Split large methods into smaller ones and apply SOLID principles.
   - Implement proper error handling and boundary condition checks.

2. **Enhance Configuration Management**:
   - Replace global configuration with explicit parameter passing or environment variables.

3. **Implement Unit Tests**:
   - Write comprehensive unit tests for all major components to ensure correctness and coverage.

4. **Document Public Interfaces**:
   - Add docstrings and comments to explain the purpose and usage of public methods.