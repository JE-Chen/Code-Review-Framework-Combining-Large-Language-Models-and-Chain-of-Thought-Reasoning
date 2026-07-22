### Diff #1: Function Logic and Readability Issues

---

### 1. **Summary**
The code contains complex nested conditionals and repetitive logic in `doSomething` and `processData`. The main function has print statements and hardcoded values, reducing clarity and testability. The code lacks separation of concerns and explicit error handling.

---

### 2. **Linting Issues**
- **Spacing and formatting**: Missing space after commas and operators.
- **Variable names**: `val` in `main` is unclear; `result` is better.
- **Unused variables**: `y` in `main` is never used.
- **Print statements**: Hardcoded logs reduce testability.

---

### 3. **Code Smells**
- **Tight coupling**: `doSomething` performs multiple tasks (validation, computation, I/O), making it hard to test.
- **Overly complex logic**: `doSomething` has 12+ conditionals, increasing cognitive load.
- **Redundant print statements**: Hardcoded logs reduce readability and testability.
- **Poor naming**: `val` in `main` lacks context.

---

### Recommendations
- Refactor `doSomething` into smaller functions.
- Use explicit return values and avoid print statements.
- Add docstrings and test cases for edge cases.