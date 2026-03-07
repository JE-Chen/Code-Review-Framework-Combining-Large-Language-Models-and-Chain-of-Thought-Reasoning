### 1. **Global Variables Used (no-global-variables)**
- **Issue:** The code uses global variables like `dataFrameLike`, `resultCache`, etc., which reduce modularity and testability.
- **Explanation:** When functions rely on or modify global state, it becomes hard to predict behavior, especially during testing or refactoring.
- **Root Cause:** The design assumes all functions have access to shared data, breaking encapsulation.
- **Impact:** Makes debugging harder and increases risk of side effects.
- **Fix:** Refactor to use local variables or pass dependencies as parameters. Example:
  ```python
  def analyze_data(data_frame_like, result_cache):
      # process data
      return processed_result
  ```

---

### 2. **Duplicate Computation (no-duplicate-code)**
- **Issue:** The function `analyzeData()` computes `statistics.median(vals)` twice unnecessarily.
- **Explanation:** Repeated calculations waste resources and complicate future updates.
- **Root Cause:** Lack of temporary variable usage to store intermediate results.
- **Impact:** Slight performance degradation; harder to maintain consistency.
- **Fix:** Store the computed value once and reuse it:
  ```python
  median_val = statistics.median(vals)
  resultCache['median'] = median_val
  ...
  resultCache['another_median'] = median_val
  ```

---

### 3. **Magic Numbers (no-magic-numbers)**
- **Issue:** Hardcoded numbers like `5`, `10`, `50` are used without explanation.
- **Explanation:** These numbers make code less readable and harder to change later.
- **Root Cause:** No abstraction or naming for key numeric values.
- **Impact:** Reduces maintainability; future developers won’t know what the numbers mean.
- **Fix:** Replace with named constants:
  ```python
  THRESHOLD_LOW = 5
  THRESHOLD_HIGH = 10
  MAX_ROWS = 50
  ```

---

### 4. **Unnecessary Ternary Operator (no-unneeded-ternary)**
- **Issue:** A ternary expression is used where a direct assignment would work fine.
- **Explanation:** Overcomplicates logic unnecessarily.
- **Root Cause:** Inefficient use of conditional syntax.
- **Impact:** Minor readability issue; can be confusing for newcomers.
- **Fix:** Simplify the condition:
  ```python
  if condition:
      severity = 'HIGH'
  else:
      severity = 'LOW'
  ```

---

### 5. **Side Effects in Functions (no-side-effects-in-functions)**
- **Issue:** Functions like `generateData`, `showData` alter global state directly.
- **Explanation:** Functions should ideally not mutate external state unless explicitly designed to do so.
- **Root Cause:** Mixing business logic with UI interaction.
- **Impact:** Reduces testability and reusability.
- **Fix:** Return data instead of modifying global variables:
  ```python
  def generate_data():
      return [1, 2, 3]  # Return data instead of updating global var
  ```

---

### 6. **Empty Block / Missing Error Handling (no-empty-blocks)**
- **Issue:** An `else` block exists but does not provide meaningful feedback when no data is present.
- **Explanation:** Edge cases should be handled gracefully, not ignored silently.
- **Root Cause:** Lack of proper error reporting or logging in edge conditions.
- **Impact:** Makes troubleshooting harder.
- **Fix:** Add logging or informative messages:
  ```python
  else:
      print("No data available for analysis.")
      # Or log to file
  ```

--- 

### Summary of Recommendations:

| Issue | Priority | Recommendation |
|-------|----------|----------------|
| Global Variable Usage | High | Move variables into local scope or classes |
| Duplicate Computation | Medium | Cache expensive operations |
| Magic Numbers | Medium | Replace with descriptive constants |
| Unneeded Ternary | Medium | Use straightforward assignments |
| Side Effects | High | Avoid modifying global state inside functions |
| Empty/Untested Blocks | Medium | Add logging or informative error handling |

### Best Practices:
- **DRY Principle**: Avoid repeating logic.
- **Single Responsibility Principle**: Each function should do one thing well.
- **Encapsulation**: Hide internal state from outside functions.
- **Naming Consistency**: Use clear, descriptive names for variables and functions.
- **Testability**: Design modules so they can be tested independently.