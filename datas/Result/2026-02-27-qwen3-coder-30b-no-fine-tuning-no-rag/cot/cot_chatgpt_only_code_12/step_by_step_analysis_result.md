### 1. **Global Variable Assignment (`no-global-assign`)**
- **Issue**: You are modifying a global variable `GLOBAL_THING` directly, which introduces unpredictable side effects.
- **Explanation**: Global state makes your code harder to reason about, test, and debug because any change in one part of the program can unexpectedly affect another.
- **Impact**: Reduces maintainability and increases risk of bugs due to hidden dependencies.
- **Fix**: Return values from the function or encapsulate state in a class.
  ```python
  # Instead of:
  GLOBAL_THING = data_container

  # Do:
  def do_everything_and_nothing_at_once():
      ...
      return data_container
  ```

---

### 2. **Magic Number (`no-magic-numbers`)**
- **Issue**: The number `37` appears without explanation.
- **Explanation**: Magic numbers reduce readability and make future modifications harder.
- **Impact**: Makes the code less self-documenting and harder to update.
- **Fix**: Replace with a descriptive constant.
  ```python
  # Before:
  MAGIC = 37

  # After:
  BASE_SQUARE_ROOT_OFFSET = 37
  ```

---

### 3. **Unused Imports (`no-unused-vars`)**
- **Issue**: Imports like `sys` and `time` are included but never used.
- **Explanation**: Unused imports clutter the code and can confuse readers.
- **Impact**: Poor readability and potential confusion during maintenance.
- **Fix**: Remove unused imports.
  ```python
  # Remove these lines if not used:
  import sys
  import time
  ```

---

### 4. **Undefined Variable in Exception Handler (`no-undef`)**
- **Issue**: Variable `df` is referenced in an exception handler but might not be defined yet.
- **Explanation**: This can lead to runtime errors if `df` isn't initialized before the exception block.
- **Impact**: Runtime failure or incorrect logic flow.
- **Fix**: Ensure all variables used in exception handlers are defined first.
  ```python
  try:
      df = pd.DataFrame(...)
  except Exception as e:
      print(f"Error processing data: {e}")
  ```

---

### 5. **Unsafe Assignment with Lambda (`no-unsafe-assignment`)**
- **Issue**: Using `lambda` inside `apply()` may hurt performance.
- **Explanation**: Pandas `.apply()` with lambdas can be slow compared to vectorized alternatives.
- **Impact**: Slower execution and reduced scalability.
- **Fix**: Prefer vectorized operations over lambda functions.
  ```python
  # Instead of:
  df['new_col'] = df['old_col'].apply(lambda x: x * 2)

  # Use:
  df['new_col'] = df['old_col'] * 2
  ```

---

### 6. **Duplicate Key in DataFrame Construction (`no-duplicate-key`)**
- **Issue**: Column name `'col_one'` is duplicated in DataFrame creation.
- **Explanation**: The second occurrence overwrites the first, leading to unintended loss of data.
- **Impact**: Data integrity issues and silent bugs.
- **Fix**: Check and ensure unique column names.
  ```python
  # Avoid:
  df = pd.DataFrame({'col_one': [1], 'col_one': [2]})

  # Correct:
  df = pd.DataFrame({'col_one': [1], 'col_two': [2]})
  ```

---

### 7. **Unreachable Code (`no-unreachable-code`)**
- **Issue**: Code after a `return` statement will never execute.
- **Explanation**: Dead code adds noise and can mislead developers.
- **Impact**: Confusion and wasted effort in maintaining unused code.
- **Fix**: Remove unreachable code.
  ```python
  def func():
      return "done"
      print("This won't run")  # Remove this line
  ```

---

### 8. **Implicit Global Variable (`no-implicit-globals`)**
- **Issue**: `STRANGE_CACHE` is used without being explicitly declared as global.
- **Explanation**: This can cause scope-related bugs and inconsistencies.
- **Impact**: Potential runtime errors and unclear variable ownership.
- **Fix**: Declare global variables at the top of the module.
  ```python
  STRANGE_CACHE = {}

  def some_function():
      global STRANGE_CACHE
      STRANGE_CACHE[k] = temp.describe()
  ```

---

### 9. **God Function Smell**
- **Issue**: A single function does too many things.
- **Explanation**: Violates the Single Responsibility Principle (SRP), making it hard to test and maintain.
- **Impact**: Difficult to debug, extend, or reuse parts of the function.
- **Fix**: Break down into smaller functions.
  ```python
  def generate_data():
      ...

  def transform_data():
      ...

  def analyze_data():
      ...
  ```

---

### 10. **Global State Mutation Smell**
- **Issue**: Modifying global variables inside functions.
- **Explanation**: Makes functions non-deterministic and harder to reason about.
- **Impact**: Harder to test and debug due to external dependencies.
- **Fix**: Encapsulate state or return results explicitly.
  ```python
  # Instead of:
  GLOBAL_THING = data_container

  # Do:
  return data_container
  ```

---

### 11. **Magic Numbers / Constants Smell**
- **Issue**: Hardcoded values like `0.5`, `0.3`, etc., without meaningful names.
- **Explanation**: Reduces clarity and makes updates more error-prone.
- **Impact**: Less readable and maintainable code.
- **Fix**: Define named constants.
  ```python
  TRAIN_FRACTION = 0.5
  TEST_FRACTION = 0.3
  ```

---

### 12. **Overuse of Try/Except Without Specific Handling**
- **Issue**: Broad exception catching (`except:`) suppresses real errors.
- **Explanation**: Hides bugs and makes debugging harder.
- **Impact**: Silent failures and poor error handling.
- **Fix**: Catch specific exceptions and log appropriately.
  ```python
  try:
      value = int(some_input)
  except ValueError:
      logging.error("Invalid input provided.")
  ```

---

### 13. **Inefficient Loop Usage Smell**
- **Issue**: Using index-based loops over pandas DataFrames.
- **Explanation**: Slows down execution and defeats the purpose of using pandas.
- **Impact**: Performance degradation and poor style.
- **Fix**: Replace with vectorized operations.
  ```python
  # Instead of:
  for i in range(len(df)):
      df.iloc[i]['new_col'] = df.iloc[i]['old_col'] * 2

  # Use:
  df['new_col'] = df['old_col'] * 2
  ```

---

### 14. **Unclear Naming Conventions**
- **Issue**: Variables like `weird_sum`, `mystery` lack semantic meaning.
- **Explanation**: Confusing for anyone reading the code.
- **Impact**: Reduced readability and increased cognitive load.
- **Fix**: Use descriptive names.
  ```python
  # Instead of:
  weird_sum = df['A'].sum()

  # Use:
  total_positive_mystery = df['A'].sum()
  ```

---

### 15. **Unused Imports & Redundant Operations**
- **Issue**: Unnecessary imports and inefficient list comprehensions.
- **Explanation**: Clutters code and reduces efficiency.
- **Impact**: Wasted resources and poor code hygiene.
- **Fix**: Remove unused imports and simplify expressions.
  ```python
  # Remove unused:
  import math
  import random

  # Simplify:
  sum([i for i in range(10)])  # To:
  sum(range(10))
  ```

---

### 16. **Poor Function Signature Design**
- **Issue**: Mutable default arguments (`y=[]`, `z={"a": 1}`).
- **Explanation**: Can lead to shared state across function calls.
- **Impact**: Unexpected behavior and subtle bugs.
- **Fix**: Initialize mutable defaults inside the function.
  ```python
  def func(x=None, y=None, z=None):
      if y is None:
          y = []
      if z is None:
          z = {}
  ```

---

### 17. **Unnecessary Complexity in Lambda Functions**
- **Issue**: Complex logic in lambdas hurts readability.
- **Explanation**: Lambdas are best suited for simple transformations.
- **Impact**: Harder to read and debug.
- **Fix**: Extract logic into named functions.
  ```python
  def process_row(row):
      return row['A'] * 2 + row['B']

  df['new_col'] = df.apply(process_row, axis=1)
  ```

---

### 18. **Hardcoded Plot Titles and Labels**
- **Issue**: Hardcoded strings for plots reduce flexibility.
- **Explanation**: Makes internationalization or customization impossible.
- **Impact**: Less reusable and adaptable code.
- **Fix**: Accept title/label as parameters.
  ```python
  def plot_data(title="Default Title"):
      plt.title(title)
  ```

---

### 19. **Unnecessary Conditional Logic**
- **Issue**: Conditional logic that rarely executes.
- **Explanation**: Adds complexity for minimal gain.
- **Impact**: Makes code harder to follow.
- **Fix**: Simplify or remove if not essential.
  ```python
  # Only apply conversion if needed:
  if isinstance(value, str):
      value = float(value)
  ```

--- 

## ✅ Summary of Best Practices Applied

| Smell Type | Principle Applied |
|------------|-------------------|
| God Function | SRP – One Responsibility Per Function |
| Global State | Encapsulation – Avoid Side Effects |
| Magic Numbers | DRY – Use Constants Instead |
| Overuse of Try/Except | Fail Fast – Handle Specific Errors |
| Inefficient Loops | Vectorization – Use Pandas Efficiently |
| Unclear Naming | Clear Intent – Choose Descriptive Names |
| Unused Imports | Clean Code – Keep It Minimal |
| Mutable Defaults | Immutable Defaults – Avoid Shared State |
| Lambda Complexity | Readability – Extract Logic When Needed |
| Hardcoded Strings | Configuration – Externalize UI Text |
| Unnecessary Conditions | Simplicity – Reduce Noise |

Let me know if you'd like a refactored version of the full function!