### Code Smell Type: Global Variables
- **Problem Location**:  
  Global variables `DATAFRAME`, `resultList`, and `tempStorage` declared at module level, with `global` declarations in all functions accessing them.
- **Detailed Explanation**:  
  Global state creates hidden dependencies and tight coupling, making the code non-deterministic and impossible to test in isolation. For example, `calcStats` relies on `DATAFRAME` being set by `loadData`, but if `DATAFRAME` is modified elsewhere, behavior becomes unpredictable. This violates encapsulation and complicates debugging.
- **Improvement Suggestions**:  
  Replace global state with explicit function parameters and return values. Refactor to:  
  ```python
  def load_data():
      return pd.DataFrame({ ... })
  
  def calculate_stats(df):
      results = {}
      for col in df.columns:
          if col in ["A", "B"]:
              mean = st.mean(df[col])
              results[col] = {"mean": mean}
      return results
  
  def plot_data(df):
      fig, ax = plt.subplots()
      ax.hist(df["A"], bins=7)
      # ... 
  ```
- **Priority Level**: High  

---

### Code Smell Type: Violation of Single Responsibility Principle
- **Problem Location**:  
  `calcStats` handles statistics calculation, result aggregation, and side-effect storage (`resultList`, `tempStorage`).
- **Detailed Explanation**:  
  This function performs multiple unrelated tasks:  
  1. Column-specific logic (A/B)  
  2. Result accumulation  
  3. Global state mutation  
  This makes the function complex, error-prone (e.g., redundant mean calculation for column "A"), and impossible to reuse or test independently.
- **Improvement Suggestions**:  
  Split responsibilities:  
  ```python
  def calculate_column_stats(df, column):
      """Calculate mean for a column (or handle special cases)."""
      return st.mean(df[column])
  
  def generate_results(df):
      """Return structured results without side effects."""
      return {
          "meanA": calculate_column_stats(df, "A"),
          "meanB": calculate_column_stats(df, "B"),
          "dummy": len(df["C"])
      }
  ```
- **Priority Level**: High  

---

### Code Smell Type: Redundant Operations
- **Problem Location**:  
  In `calcStats`, column "A" mean is calculated twice:  
  ```python
  meanA = st.mean(DATAFRAME[col])
  # ...
  resultList.append(("meanA_again", st.mean(DATAFRAME[col])))  # Redundant
  ```
- **Detailed Explanation**:  
  Same calculation repeated for `meanA` and `meanA_again`, wasting CPU cycles and confusing readers. This suggests poor planning (likely a copy-paste error).
- **Improvement Suggestions**:  
  Remove redundant operation:  
  ```python
  # Replace with:
  resultList.append(("meanA", meanA))
  # Remove the duplicate calculation
  ```
- **Priority Level**: Low  

---

### Code Smell Type: Hard-coded Column Logic
- **Problem Location**:  
  `calcStats` uses hardcoded column checks:  
  ```python
  if col in ["A", "B"]:
      if col == "A": ... 
      else: ... 
  ```
- **Detailed Explanation**:  
  The code assumes columns "A" and "B" exist and are handled identically. Adding new columns requires modifying this function, violating open/closed principle. Also, the `else` clause for non-A/B columns is under-specified.
- **Improvement Suggestions**:  
  Use a configuration-driven approach:  
  ```python
  COLUMN_PROCESSING = {
      "A": lambda df: ("meanA", st.mean(df["A"])),
      "B": lambda df: ("meanB", st.mean(df["B"])),
      # Add new columns without modifying logic
  }
  
  def calculate_stats(df):
      return [func(df) for col, func in COLUMN_PROCESSING.items() if col in df.columns]
  ```
- **Priority Level**: Medium  

---

### Code Smell Type: Lack of Documentation
- **Problem Location**:  
  Zero docstrings for functions or key variables.
- **Detailed Explanation**:  
  Functions like `calcStats` and `plotData` lack clarity on purpose, inputs, outputs, or side effects. For example, `calcStats` appends to `resultList` but doesn’t document why or how the results are structured.
- **Improvement Suggestions**:  
  Add concise docstrings:  
  ```python
  def calcStats(df):
      """Calculate column statistics and return results.
      
      Args:
          df (pd.DataFrame): Input DataFrame with columns "A", "B", "C".
      
      Returns:
          list[tuple]: (statistic_name, value)
      """
      # ...
  ```
- **Priority Level**: Medium  

---

### Code Smell Type: Magic Number in Plotting
- **Problem Location**:  
  `ax.hist(DATAFRAME["A"], bins=7)` uses unexplained `bins=7`.
- **Detailed Explanation**:  
  The number 7 is arbitrary and undocumented. If the bin count needs adjustment, the magic number must be searched for in code.
- **Improvement Suggestions**:  
  Replace with a constant or parameter:  
  ```python
  HIST_BINS = 7  # Documented reason (e.g., "Optimal for dataset size")
  ax.hist(df["A"], bins=HIST_BINS)
  ```
- **Priority Level**: Low