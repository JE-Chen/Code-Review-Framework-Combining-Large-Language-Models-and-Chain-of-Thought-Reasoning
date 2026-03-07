- **Naming & Readability**:  
  Use snake_case for variables (e.g., `meanVal` → `mean_value`). Global variables `DATA` and `RESULTS` should be avoided in Flask; use request context or dependency injection instead.

- **Redundant Logic**:  
  `statistics.mean(DATA)` is computed twice in `/analyze` (for `mean` and `meanAgain`). Compute once and reuse.

- **Inconsistent Conditions**:  
  The `if len(DATA) > 5` block sets `mean` and `meanAgain` (redundant), while `median` is only set for `>10`. Clarify intent with comments or refactor.

- **Missing Documentation**:  
  No docstrings for routes or key logic (e.g., why `meanAgain` exists, why median is delayed).

- **Global State Risk**:  
  Using global variables (`DATA`, `RESULTS`) breaks thread safety in production. This will cause race conditions under load.

- **Security Note**:  
  No input validation (though harmless here), but avoid global state for security-critical data.