- **Hardcoded Threshold in `filter_high_scores`**: The condition `s > 40` uses a magic number instead of the config-defined threshold. Replace with `s > DATA["config"]["threshold"]` to avoid inconsistency (config threshold is 50, but hardcoded 40 is incorrect).
  
- **Potential Division by Zero**: `calculate_average_scores` lacks validation for empty `scores` lists, risking `ZeroDivisionError` (e.g., if a user had no scores). Add a guard clause or ensure data integrity.

- **Global State Dependency**: All functions rely on the global `DATA` dictionary, reducing testability and reusability. Pass `DATA` as a parameter to functions instead.

- **Ambiguous Variable Name**: `s` in `filter_high_scores` is too cryptic. Rename to `score` for clarity and maintainability.

- **Missing Function Documentation**: No docstrings describe purpose, parameters, or return values. Add brief summaries for all functions to improve readability.