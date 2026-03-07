1. **Code Smell: No Global Variables**
   - **Issue**: Uses global variables `GLOBAL_THING` and `STRANGE_CACHE`.
   - **Explanation**: Global state introduces tight coupling and makes behavior unpredictable.
   - **Impact**: Harder to test, debug, and reason about code.
   - **Fix**: Pass shared state explicitly or encapsulate in a class.
     ```python
     def process_data(data, cache=None):
         # Avoid modifying global state
     ```

2. **Code Smell: Magic Numbers**
   - **Issue**: Hardcoded value `37` used directly.
   - **Explanation**: Unclear purpose of the number.
   - **Impact**: Reduces readability and maintainability.
   - **Fix**: Replace with a descriptive constant.
     ```python
     MAX_ITERATIONS = 37
     ```

3. **Code Smell: Dangerous Defaults**
   - **Issue**: Mutable defaults `y=[]` and `z={"a": 1}`.
   - **Explanation**: Shared reference causes unexpected behavior.
   - **Impact**: Bugs due to shared mutable state.
   - **Fix**: Default to `None`, initialize inside function.
     ```python
     def func(y=None, z=None):
         y = y or []
         z = z or {}
     ```

4. **Code Smell: Unnecessary Loop**
   - **Issue**: Looping over `range(len(df))`.
   - **Explanation**: Less efficient than vectorized operations.
   - **Impact**: Slower performance and reduced clarity.
   - **Fix**: Use vectorized methods.
     ```python
     df['new_col'] = df['col'].apply(lambda x: x * 2)
     ```

5. **Code Smell: Broad Exception Handling**
   - **Issue**: Empty `except:` blocks.
   - **Explanation**: Silently ignores errors.
   - **Impact**: Hidden bugs and debugging difficulties.
   - **Fix**: Log or re-raise exceptions.
     ```python
     except Exception as e:
         logger.exception("Error occurred")
         raise
     ```

6. **Code Smell: Redundant Calculation**
   - **Issue**: Recomputing `df['mystery']` repeatedly.
   - **Explanation**: Wasteful computation inside loops.
   - **Impact**: Performance degradation.
   - **Fix**: Precompute outside loop.
     ```python
     mystery = df['mystery']
     for row in df.itertuples():
         val = mystery[row.Index]
     ```

7. **Code Smell: Unexpected Side Effects**
   - **Issue**: Function modifies global `GLOBAL_THING`.
   - **Explanation**: Modifies external state unexpectedly.
   - **Impact**: Hard to predict function behavior.
   - **Fix**: Return new values instead of mutating.
     ```python
     updated_global = update_global_state(current_state)
     ```

8. **Code Smell: Inconsistent Return Types**
   - **Issue**: Return type depends on condition.
   - **Explanation**: Makes API unclear.
   - **Impact**: Difficult to consume reliably.
   - **Fix**: Ensure consistent return types.
     ```python
     if condition:
         return True
     else:
         return False  # Always same type
     ```

9. **Code Smell: Complex Nested Logic**
   - **Issue**: Deep nesting and multiple conditionals.
   - **Explanation**: Increases complexity and reduces readability.
   - **Impact**: Hard to follow logic.
   - **Fix**: Extract logic into helper functions.
     ```python
     def helper_logic():
         pass
     ```

10. **Code Smell: Confusing Naming**
    - **Issue**: Function name `do_everything_and_nothing_at_once`.
    - **Explanation**: Doesn’t describe functionality well.
    - **Impact**: Misleading and hard to understand.
    - **Fix**: Use clear and descriptive names.
      ```python
      def process_synthetic_data_analysis():
          pass
      ```

11. **Code Smell: Side Effects in List Comprehension**
    - **Issue**: Using list comprehension for side effect.
    - **Explanation**: Misuse of syntax.
    - **Impact**: Confusion and violation of expectation.
    - **Fix**: Use explicit loop.
      ```python
      for i in range(10):
          print(i)
      ```

12. **Code Smell: Overuse of Lambda**
    - **Issue**: Complex logic in lambda.
    - **Explanation**: Makes code less readable.
    - **Impact**: Reduced maintainability.
    - **Fix**: Replace with named function.
      ```python
      def complex_func(x):
          return x * 2 + 1
      ```

13. **Code Smell: Artificial Delays**
    - **Issue**: `time.sleep(0.01)` in loops.
    - **Explanation**: Adds unnecessary delay.
    - **Impact**: Poor responsiveness.
    - **Fix**: Remove unless necessary for async/testing.
      ```python
      # Remove sleep call
      ```

14. **Code Smell: Unused Imports**
    - **Issue**: Imported but unused modules (`sys`, `math`, `random`).
    - **Explanation**: Clutter and confusion.
    - **Impact**: Cleaner codebase.
    - **Fix**: Remove unused imports.
      ```python
      import pandas as pd  # Only what’s used
      ```