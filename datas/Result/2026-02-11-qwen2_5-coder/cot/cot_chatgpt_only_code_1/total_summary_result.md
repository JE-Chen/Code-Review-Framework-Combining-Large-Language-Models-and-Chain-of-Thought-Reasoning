## PR Total Summary

### Overall Conclusion
The PR introduces significant improvements but contains some critical issues that block merging. Key concerns include inconsistent naming, lack of modularity, and global state usage.

### Comprehensive Evaluation
- **Code Quality and Correctness**: The code refactoring improves readability and correctness. However, it still contains global state and implicit type handling.
- **Maintainability and Design Concerns**: The code lacks proper separation of concerns and suffers from magic numbers and redundant assignments.
- **Consistency with Existing Patterns or Standards**: The refactoring aligns with some standards but fails to eliminate global state and redundant code.

### Final Decision Recommendation
**Request changes**

Justification:
- The code still relies on global state (`total_result`) and implicit type handling, which undermines maintainability.
- There are significant areas for further refactoring to achieve clean, modular code.
- Additional tests and documentation are needed to ensure the code is fully tested and understandable.

### Team Follow-Up
- Refactor out the global variable `total_result` and pass it explicitly between functions.
- Introduce named constants for magic numbers.
- Write comprehensive unit tests for each function to cover edge cases.
- Ensure all functions have clear docstrings describing their purpose, parameters, and return values.