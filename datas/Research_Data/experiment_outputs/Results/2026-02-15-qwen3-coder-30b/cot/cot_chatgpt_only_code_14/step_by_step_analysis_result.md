### 1. **Global Mutable State Usage**
- **Issue:** The code relies on global variables (`GLOBAL_DATA_THING`, `GLOBAL_FLAG`) to pass data and control behavior between functions.
- **Explanation:** This creates tight coupling and hidden dependencies. Testing becomes difficult because the behavior depends on external mutable state.
- **Impact:** Reduces modularity, makes debugging harder, and increases chances of side effects.
- **Fix:** Pass state explicitly through parameters or encapsulate it in a class.
  ```python
  # Instead of using global variables
  def process_data():
      global GLOBAL_FLAG
      GLOBAL_FLAG = True

  # Do this instead:
  class DataProcessor:
      def __init__(self):
          self.flag = False

      def process(self):
          self.flag = True
  ```
- **Best Practice:** Prefer dependency injection over global state.

---

### 2. **Unused Variable**
- **Issue:** The variable `MAGIC_NUMBER` is declared but never used beyond its definition.
- **Explanation:** Leftover constants can confuse readers and clutter code.
- **Impact:** Minor maintenance burden; no functional harm.
- **Fix:** Either remove the unused constant or use it for clarity.
  ```python
  # Remove unused
  MAGIC_NUMBER = 42  # <- Remove if not used
  ```
- **Best Practice:** Regularly audit code for dead code.

---

### 3. **Catch-All Exception Handling**
- **Issue:** Broad `except:` clauses hide unexpected errors.
- **Explanation:** When catching all exceptions, developers lose visibility into real bugs.
- **Impact:** Debugging becomes harder, and silent failures may occur.
- **Fix:** Catch specific exceptions or at least log them before re-raising.
  ```python
  # Bad
  try:
      risky_operation()
  except:
      pass

  # Good
  try:
      risky_operation()
  except ValueError as e:
      logger.error(f"Invalid input: {e}")
      raise
  ```
- **Best Practice:** Be explicit about which errors are handled.

---

### 4. **Magic Numbers**
- **Issue:** Hard-coded numeric literals like `0.0001` and `0.7` lack semantic meaning.
- **Explanation:** These values make assumptions unclear and reduce readability.
- **Impact:** Difficult to change or reason about behavior later.
- **Fix:** Define meaningful names for such values.
  ```python
  TOLERANCE_THRESHOLD = 0.0001
  CONFIDENCE_LEVEL = 0.7
  ```
- **Best Practice:** Replace magic numbers with named constants.

---

### 5. **Side Effects Without Contract**
- **Issue:** Functions modify global flags without declaring intent.
- **Explanation:** Changes to global state are not obvious from function signatures.
- **Impact:** Makes behavior unpredictable and hard to test.
- **Fix:** Make side effects visible through parameters or returns.
  ```python
  # Instead of modifying global flag
  def update_flag(flag_value):
      return flag_value

  # Use return or explicit parameter passing
  updated_flag = update_flag(current_flag)
  ```
- **Best Practice:** Avoid side effects unless necessary and documented.

---

### 6. **Poor Method Names**
- **Issue:** Method names like `make_data_somehow` and `analyze_in_a_hurry` are vague.
- **Explanation:** Vague names obscure purpose and make understanding harder.
- **Impact:** Decreases code readability and maintainability.
- **Fix:** Rename methods to reflect precise actions.
  ```python
  # Bad
  def make_data_somehow():
      ...

  # Good
  def generate_sample_dataframe():
      ...
  ```
- **Best Practice:** Choose descriptive, action-oriented names.

---

### 7. **Single Responsibility Violation**
- **Issue:** Methods perform too many unrelated tasks.
- **Explanation:** Complex functions are hard to test, debug, and reuse.
- **Impact:** Increases complexity and risk of bugs.
- **Fix:** Split large methods into smaller, focused ones.
  ```python
  # Before
  def process_and_visualize(df):
      df['new_col'] = df['old_col'] * 2
      plot_histogram(df)
      save_results(df)

  # After
  def transform_dataframe(df):
      return df.assign(new_col=df['old_col'] * 2)

  def visualize(df):
      plot_histogram(df)

  def export_results(df):
      save_results(df)
  ```
- **Best Practice:** Each function should do one thing well.

---

### 8. **UI Logic Mixed With Core Logic**
- **Issue:** Business logic includes direct UI updates.
- **Explanation:** Mixing presentation and domain logic leads to tight coupling.
- **Impact:** Harder to test or reuse logic outside of GUI context.
- **Fix:** Separate concerns—keep core logic independent.
  ```python
  # Bad
  def compute_result(data):
      ui.update_progress_bar(50)
      return result

  # Better
  def compute_result(data):
      return result

  # Handle UI update separately
  def on_compute_complete(result):
      ui.update_progress_bar(100)
  ```
- **Best Practice:** Follow separation of concerns.

---

### 9. **Unnecessary Sleep Calls**
- **Issue:** Artificial delays (`time.sleep(...)`) added for no benefit.
- **Explanation:** Adds latency without improving correctness.
- **Impact:** Misleading or unnecessary delays in execution.
- **Fix:** Remove unless part of simulation or async behavior.
  ```python
  # Remove sleep calls unless needed
  time.sleep(0.05)  # Remove if not essential
  ```
- **Best Practice:** Only add timing when strictly necessary.

---

### 10. **Unused Imports**
- **Issue:** Imports like `math`, `numpy`, `matplotlib` are imported but not fully used.
- **Explanation:** Cluttered import list confuses developers.
- **Impact:** Minor readability impact.
- **Fix:** Clean up unused imports.
  ```python
  # Remove unused
  import math  # Remove if not used
  import numpy as np  # Remove if not used
  ```
- **Best Practice:** Keep imports clean and relevant.