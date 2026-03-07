**Diff #1**

### Summary
This diff introduces several new functions (`calculate_average_scores`, `filter_high_scores`, `process_misc`) that process data stored in a global dictionary called `DATA`. The `main` function calls these functions and prints their results.

### Linting Issues
- **PEP 8**: Variable names should be lowercase with words separated by underscores (e.g., `DATA` should be renamed to `data`).  
  - *File: code.py*, *Line: 1*
- **PEP 8**: Function names should be lowercase with words separated by underscores (e.g., `calculate_average_scores` should be renamed to `calculate_average_scores`).  
  - *File: code.py*, *Lines: 5, 11, 17*

### Code Smells
- **Long Functions**: Each function performs a single task but could benefit from further decomposition.
  - *Functions*: `calculate_average_scores`, `filter_high_scores`, `process_misc`
- **Tight Coupling**: Functions depend on global variables (`DATA`, `config`), which makes them harder to test and reuse.
  - *Functions*: All functions except `main`
- **Magic Numbers**: Hardcoded values like `40` and `50` are used without explanation.
  - *File: code.py*, *Lines: 12, 18, 25*