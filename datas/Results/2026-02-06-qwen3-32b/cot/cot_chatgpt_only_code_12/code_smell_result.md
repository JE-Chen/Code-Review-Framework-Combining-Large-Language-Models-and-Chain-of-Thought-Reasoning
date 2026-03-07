### Code Smell Type: Poorly Named Global Variables
- **Problem Location**: 
  ```python
  GLOBAL_THING = None
  STRANGE_CACHE = {}
  MAGIC = 37
  ```
- **Detailed Explanation**: 
  Global variables (`GLOBAL_THING`, `STRANGE_CACHE`, `MAGIC`) are poorly named and lack semantic meaning. `GLOBAL_THING` implies no purpose, `STRANGE_CACHE` suggests undocumented behavior, and `MAGIC` is a classic magic number. These introduce hidden coupling, make code hard to test, and violate RAG rules against shared mutable state. Global state also breaks referential transparency and complicates parallel execution.
- **Improvement Suggestions**: 
  - Replace global state with explicit parameters/return values. For example:
    ```python
    # Remove GLOBAL_THING entirely
    # Instead, return data_container as part of the result
    return df, result, data_container  # Caller manages state
    ```
  - Replace `MAGIC` with a descriptive constant:
    ```python
    MATH_CONSTANT = 37  # Document why 37 is used
    ```
  - Remove `STRANGE_CACHE` and handle caching via function parameters or a dedicated cache object.
- **Priority Level**: High

---

### Code Smell Type: Mutable Default Arguments
- **Problem Location**: 
  ```python
  def do_everything_and_nothing_at_once(x=None, y=[], z={"a": 1}):
  ```
- **Detailed Explanation**: 
  Using mutable defaults (`y=[]`, `z={"a": 1}`) violates Python best practices. The same list/dict is shared across all function calls, leading to unexpected side effects (e.g., appending to `y` in one call affects subsequent calls). This is a critical bug risk and violates RAG rules against hidden state mutations.
- **Improvement Suggestions**: 
  - Replace with `None` defaults and initialize inside the function:
    ```python
    def do_everything_and_nothing_at_once(x=None, y=None, z=None):
        y = y or []
        z = z or {"a": 1}
    ```
- **Priority Level**: High

---

### Code Smell Type: Violation of Single Responsibility Principle
- **Problem Location**: Entire function body
- **Detailed Explanation**: 
  The function handles data generation, analysis, visualization, and side effects (plotting, global mutation). This violates SRP, making the function:
  - Hard to test (requires mocking global state, I/O, and randomness)
  - Impossible to reuse (e.g., can't extract analysis without plotting)
  - Prone to bugs (e.g., `GLOBAL_THING` assignment conflicts with return values)
  RAG rules explicitly require splitting responsibilities into focused functions.
- **Improvement Suggestions**: 
  Split into atomic functions:
  ```python
  def generate_data(x: int) -> list[float]: ...
  def analyze_dataframe(df: pd.DataFrame) -> dict: ...
  def plot_analysis(df: pd.DataFrame) -> None: ...
  ```
  Each function should have one clear purpose and avoid side effects.
- **Priority Level**: High

---

### Code Smell Type: Broad Exception Handling
- **Problem Location**: 
  ```python
  try:
      value = float(str(value))
  except:
      pass
  ```
  and
  ```python
  for i in range(len(df)):
      try:
          ...
      except Exception as e:
          weird_sum += 0
  ```
- **Detailed Explanation**: 
  Catching all exceptions (`except:`) and ignoring errors (e.g., `pass`, `weird_sum += 0`) masks bugs and prevents debugging. The first block silently drops errors when converting to float, while the second swallows all exceptions. This violates RAG rules against broad exception handling and makes errors undetectable.
- **Improvement Suggestions**: 
  - Remove broad `except` blocks. Handle specific exceptions or fix the root cause:
    ```python
    # Instead of try/except for conversion, validate input:
    if isinstance(value, (int, float)):
        value = float(value)
    ```
  - For the `weird_sum` loop, replace with vectorized operations (see next point) to avoid exceptions entirely.
- **Priority Level**: Medium

---

### Code Smell Type: Inefficient Loops and Vectorization
- **Problem Location**: 
  ```python
  for i in range(len(df)):
      if df.iloc[i]["mystery"] > 0:
          weird_sum += df.iloc[i]["mystery"]
      else:
          weird_sum += abs(df.iloc[i]["col_three"])
  ```
- **Detailed Explanation**: 
  Using `df.iloc[i]` in a loop is inefficient (O(n) vs. O(1) for vectorized ops) and violates RAG rules against unnecessary work in loops. The loop could be replaced with vectorized operations (e.g., `np.where`), avoiding the loop entirely. The exception handling further compounds the inefficiency.
- **Improvement Suggestions**: 
  Replace with vectorized code:
  ```python
  # Calculate weird_sum in one line
  weird_sum = df.apply(
      lambda row: row["mystery"] if row["mystery"] > 0 else abs(row["col_three"]),
      axis=1
  ).sum()
  ```
  Remove the `try` block since column existence should be guaranteed.
- **Priority Level**: Medium

---

### Code Smell Type: Magic Numbers and Ambiguous Names
- **Problem Location**: 
  ```python
  MAGIC = 37
  counter % 5 == 0
  ```
- **Detailed Explanation**: 
  `MAGIC` is a magic number without context. The number `5` (in `counter % 5`) is also arbitrary. These reduce readability and make maintenance harder. RAG rules explicitly require replacing magic numbers with descriptive constants.
- **Improvement Suggestions**: 
  ```python
  # Replace MAGIC with:
  MATH_CONSTANT = 37  # Documented reason: "Used in sqrt adjustment per spec v2.1"
  
  # Replace 5 with:
  MODULO_THRESHOLD = 5  # "Every 5th value requires string conversion"
  ```
- **Priority Level**: Low

---

### Code Smell Type: Unnecessary Side Effects
- **Problem Location**: 
  ```python
  time.sleep(0.01)
  plt.show()
  ```
- **Detailed Explanation**: 
  The `time.sleep` adds unexplained delay, and `plt.show()` forces a UI block. Both are side effects that make the function non-deterministic and hard to test. RAG rules prohibit unnecessary I/O or blocking operations in core logic.
- **Improvement Suggestions**: 
  - Remove `time.sleep` (no justification).
  - Move plotting to a separate function that the caller invokes:
    ```python
    def plot_analysis(df: pd.DataFrame) -> None:
        plt.figure()
        # ... plotting code ...
        plt.show()
    ```
- **Priority Level**: Low

---

### Code Smell Type: Inconsistent Return Types
- **Problem Location**: 
  ```python
  result = {
      "mean": df["mystery"].mean(),
      "std": df["mystery"].std(),
      "max": max(df["mystery"]),
      "min": min(df["mystery"]),
      "something_useless": sum([i for i in range(10)])  # Always 45!
  }
  ```
- **Detailed Explanation**: 
  `"something_useless"` is a hardcoded value (sum of 0-9 = 45) with no purpose. This confuses callers and violates RAG rules against meaningless return values. The function returns a mix of meaningful and useless data.
- **Improvement Suggestions**: 
  - Remove `"something_useless"` entirely.
  - Return only analysis-relevant metrics:
    ```python
    return {
        "mean": df["mystery"].mean(),
        "std": df["mystery"].std(),
        "max": df["mystery"].max(),
        "min": df["mystery"].min()
    }
    ```
- **Priority Level**: Low