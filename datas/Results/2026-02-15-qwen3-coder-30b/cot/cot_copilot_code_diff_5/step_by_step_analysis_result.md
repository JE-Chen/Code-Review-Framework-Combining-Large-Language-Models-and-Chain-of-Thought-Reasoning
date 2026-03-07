### 1. **Global Variable Assignment Detected**
- **Issue**: The variable `GLOBAL_DF` is assigned at the module level, which introduces global state.
- **Explanation**: Global variables make code unpredictable and harder to test because their values can be changed anywhere.
- **Why It Happens**: Code assumes shared mutable state rather than explicit dependency management.
- **Impact**: Reduces maintainability and increases side effects.
- **Fix**: Pass data as arguments and return results instead of mutating globals.
  ```python
  def process_data(df):
      df['new_col'] = df['score'] * 2
      return df
  ```

---

### 2. **Unused Global Variable Found**
- **Issue**: `ANOTHER_GLOBAL` is declared but never used.
- **Explanation**: Leftover code clutters the namespace and confuses readers.
- **Why It Happens**: Lack of cleanup after refactoring or experimentation.
- **Impact**: Minor impact, but indicates poor code hygiene.
- **Fix**: Remove unused declarations.
  ```python
  # Remove this line entirely
  ANOTHER_GLOBAL = "unused"
  ```

---

### 3. **Unclear Function Name**
- **Issue**: Function name `functionThatDoesTooMuchAndIsNotClear` is vague and too long.
- **Explanation**: A good function name should express purpose clearly.
- **Why It Happens**: Function tries to do too many things at once.
- **Impact**: Makes understanding and reusing code harder.
- **Fix**: Rename to reflect a single responsibility.
  ```python
  def analyze_student_data():
      ...
  ```

---

### 4. **Magic Numbers Used**
- **Issue**: Hardcoded numbers like `20` and `50` appear in conditionals.
- **Explanation**: These values lack meaning without context.
- **Why It Happens**: Quick fixes without abstraction.
- **Impact**: Difficult to update or understand logic later.
- **Fix**: Replace with named constants.
  ```python
  MIN_AGE_THRESHOLD = 20
  MAX_AGE_THRESHOLD = 50
  ```

---

### 5. **Poor Exception Handling**
- **Issue**: Generic exception catch blocks ignore detailed error info.
- **Explanation**: Suppresses valuable debugging information.
- **Why It Happens**: Overgeneralized error handling.
- **Impact**: Bugs go unnoticed and systems become fragile.
- **Fix**: Catch specific exceptions or log them appropriately.
  ```python
  try:
      risky_operation()
  except ValueError as e:
      logger.error(f"Value error occurred: {e}")
  ```

---

### 6. **Use of Print Statements**
- **Issue**: Output is sent directly to console via `print()`.
- **Explanation**: Not suitable for production or testing environments.
- **Why It Happens**: Convenience over design.
- **Impact**: Limits flexibility in output management.
- **Fix**: Replace with logging.
  ```python
  import logging
  logging.info("Average age within acceptable range")
  ```

---

### 7. **Duplicate Logic Detected**
- **Issue**: Similar logic repeated on the same column (`Score`) using random numbers.
- **Explanation**: Repetitive code is harder to maintain.
- **Why It Happens**: Lack of abstraction.
- **Impact**: Increases chance of inconsistency.
- **Fix**: Extract reusable components.
  ```python
  def adjust_score(base_score):
      return base_score + random.randint(0, 10)
  ```

--- 

### Summary of Fixes
| Rule ID                     | Suggested Change |
|----------------------------|------------------|
| `no-global-assign`         | Avoid global mutations; pass parameters |
| `no-unused-vars`           | Delete unused variables |
| `function-name-style`      | Rename ambiguous function names |
| `no-magic-numbers`         | Replace magic numbers with constants |
| `no-bad-exception-handling`| Handle specific exceptions |
| `no-print-statements`      | Switch to logging |
| `no-duplicate-code`        | Refactor repeated logic into helpers |

---

### Best Practices Applied
- **Separation of Concerns**: Split input, processing, and output logic.
- **DRY Principle**: Avoid repeating similar operations.
- **Naming Conventions**: Use clear, descriptive names.
- **Error Handling**: Be intentional with exceptions.
- **Testability**: Reduce reliance on global state.