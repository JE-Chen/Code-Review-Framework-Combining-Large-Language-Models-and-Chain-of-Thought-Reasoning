### Diff #1 Summary
This PR introduces a simple GUI application using PySide6 for managing users. The application allows adding and deleting users, displaying their details, and showing status updates.

### Diff #1 Linting Issues
- **PEP8 Violation**: Line too long (80 characters).
  - *File*: `path/to/file.py`, *Line*: 3
  - *Fix*: Split the import statement onto multiple lines.
- **Unused Import**: `time` is imported but not used.
  - *File*: `path/to/file.py`, *Line*: 2
  - *Fix*: Remove unused import.

### Diff #1 Code Smells
- **Long Method**: `MainWindow.add_user()` and `MainWindow.delete_user()` both exceed 10 lines.
  - *Issue*: Methods should ideally do one thing only.
  - *Fix*: Refactor methods into smaller, focused functions.
- **Magic Numbers**: Hardcoded values like `0.3` and `0.2`.
  - *Issue*: Values should be defined as constants or configurable parameters.
  - *Fix*: Define these values at the top of the module.
- **Redundant Code**: Similar logic exists in `MainWindow.add_user()` and `MainWindow.delete_user()`.
  - *Issue*: Code duplication makes maintenance harder.
  - *Fix*: Extract common functionality into separate methods.