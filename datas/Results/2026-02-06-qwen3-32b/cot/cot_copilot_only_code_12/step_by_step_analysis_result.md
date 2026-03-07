### Code Quality Review

#### 1. **Naming Convention Violation: Mutable Global Variable**  
- **Issue**: Global variable `DATAFRAME` is named in uppercase (suggesting a constant) but is mutable.  
- **Root Cause**: Misuse of naming conventions for global state. Uppercase implies immutability, but the variable is reassigned.  
- **Impact**: Creates confusion about intent, risks accidental mutation, and violates Python style guidelines (PEP8).  
- **Fix**:  
  ```python
  # Before
  DATAFRAME = pd.DataFrame(...)
  
  # After
  dataframe = pd.DataFrame(...)  # snake_case, mutable
  ```
- **Best Practice**: Use `snake_case` for variables. Reserve uppercase for *true constants* (e.g., `MAX_SIZE = 100`).  

---

#### 2. **Naming Convention Violation: CamelCase Variables**  
- **Issue**: Variables `resultList` and `tempStorage` use camelCase instead of snake_case.  
- **Root Cause**: Inconsistent naming style, likely inherited from other languages (e.g., Java).  
- **Impact**: Reduces readability and violates Python conventions.  
- **Fix**:  
  ```python
  # Before
  resultList = []
  tempStorage = {}
  
  # After
  result_list = []
  temp_storage = {}
  ```
- **Best Practice**: Always use `snake_case` for variables (PEP8).  

---

#### 3. **Missing Function Docstring**  
- **Issue**: `loadData` lacks a docstring explaining purpose, inputs, and outputs.  
- **Root Cause**: Neglected documentation during implementation.  
- **Impact**: Makes code hard to understand and maintain. Other developers cannot use the function safely.  
- **Fix**:  
  ```python
  def loadData():
      """Load and return the dataset DataFrame.
      
      Returns:
          pd.DataFrame: The processed dataset.
      """
      # ... implementation
  ```
- **Best Practice**: Document all public functions (use Google-style docstrings).  

---

#### 4. **Global State Dependency**  
- **Issue**: `loadData` accesses global `DATAFRAME` without parameters.  
- **Root Cause**: Overuse of global variables instead of explicit dependencies.  
- **Impact**: Breaks testability (cannot isolate logic), causes hidden coupling, and enables unintended side effects.  
- **Fix**:  
  ```python
  # Before
  def loadData():
      global DATAFRAME
      DATAFRAME = pd.read_csv("data.csv")
  
  # After
  def load_data():
      return pd.read_csv("data.csv")
  ```
- **Best Practice**: Pass dependencies explicitly (e.g., `load_data()` returns value; caller assigns).  

---

#### 5. **Missing Function Docstring**  
- **Issue**: `calcStats` lacks a docstring.  
- **Root Cause**: Inconsistent documentation effort.  
- **Impact**: Users cannot understand the function’s behavior or structure.  
- **Fix**:  
  ```python
  def calcStats():
      """Calculate column statistics and append results to global list.
      
      Side Effects:
          Mutates global `resultList` with (statistic, value) tuples.
      """
      # ... implementation
  ```
- **Best Practice**: Document side effects and inputs/outputs.  

---

#### 6. **Global State Dependency**  
- **Issue**: `calcStats` depends on global `DATAFRAME` and `resultList`.  
- **Root Cause**: Global state used for data flow instead of parameters/return values.  
- **Impact**: Makes unit testing impossible (requires global setup) and increases bug risk.  
- **Fix**:  
  ```python
  # Before
  def calcStats():
      meanA = st.mean(DATAFRAME["A"])
      resultList.append(("meanA", meanA))
  
  # After
  def calc_stats(df):
      """Calculate column statistics and return results.
      
      Args:
          df (pd.DataFrame): Input dataset.
      
      Returns:
          list[tuple]: (statistic, value) pairs.
      """
      return [("meanA", st.mean(df["A"]))]  # No side effects
  ```
- **Best Practice**: Eliminate globals; prefer pure functions with explicit inputs/outputs.  

---

#### 7. **Redundant Calculation**  
- **Issue**: Column "A" mean calculated twice (`meanA` and `meanA_again`).  
- **Root Cause**: Copy-paste error during implementation.  
- **Impact**: Wastes CPU cycles (minor performance hit) and obscures intent.  
- **Fix**:  
  ```python
  # Before
  meanA = st.mean(DATAFRAME["A"])
  # ...
  resultList.append(("meanA_again", st.mean(DATAFRAME["A"])))  # Redundant
  
  # After
  resultList.append(("meanA", meanA))  # Use existing value
  ```
- **Best Practice**: Avoid duplicate logic; reuse computed values.  

---

#### 8. **Missing Function Docstring**  
- **Issue**: `plotData` lacks a docstring.  
- **Root Cause**: Documentation omitted for utility functions.  
- **Impact**: Users cannot understand usage or side effects (e.g., plots are rendered).  
- **Fix**:  
  ```python
  def plotData():
      """Generate and display a histogram for column 'A'.
      
      Side Effects:
          Creates a matplotlib plot (no return value).
      """
      fig, ax = plt.subplots()
      ax.hist(DATAFRAME["A"], bins=7)
      plt.show()
  ```
- **Best Practice**: Document side effects and purpose for all functions.  

---

#### 9. **Global State Dependency**  
- **Issue**: `plotData` depends on global `DATAFRAME`.  
- **Root Cause**: Global state reused instead of parameterization.  
- **Impact**: Prevents reuse (e.g., cannot plot a different dataset).  
- **Fix**:  
  ```python
  # Before
  def plotData():
      ax.hist(DATAFRAME["A"], bins=7)
  
  # After
  def plot_data(df):
      """Plot histogram for column 'A' from DataFrame.
      
      Args:
          df (pd.DataFrame): Dataset with column 'A'.
      """
      fig, ax = plt.subplots()
      ax.hist(df["A"], bins=7)
      plt.show()
  ```
- **Best Practice**: Parameterize functions instead of relying on globals.  

---

#### 10. **Missing Function Docstring**  
- **Issue**: `main` lacks a docstring.  
- **Root Cause**: Top-level script ignored documentation.  
- **Impact**: Blocks understanding of the overall workflow.  
- **Fix**:  
  ```python
  def main():
      """Execute the data pipeline: load, analyze, and visualize data."""
      df = loadData()
      stats = calcStats(df)
      plotData(df)
  ```
- **Best Practice**: Document entry points (`main()`) to clarify program flow.  

---

#### 11. **Hard-Coded Column Logic**  
- **Issue**: `calcStats` contains hardcoded column checks (`if col in ["A", "B"]`).  
- **Root Cause**: Logic tied directly to column names.  
- **Impact**: Requires code changes to add new columns (violates open/closed principle).  
- **Fix**:  
  ```python
  # Before
  if col in ["A", "B"]:
      if col == "A": ...
  
  # After
  COLUMN_PROCESSING = {
      "A": lambda df: ("meanA", st.mean(df["A"])),
      "B": lambda df: ("meanB", st.mean(df["B"]))
  }
  
  def calc_stats(df):
      return [func(df) for col, func in COLUMN_PROCESSING.items() if col in df]
  ```
- **Best Practice**: Decouple logic from data (use configuration over hard-coded rules).  

---

#### 12. **Magic Number in Plotting**  
- **Issue**: `bins=7` in `ax.hist()` lacks explanation.  
- **Root Cause**: Arbitrary value without context.  
- **Impact**: Hard to reason about or adjust bin count later.  
- **Fix**:  
  ```python
  # Before
  ax.hist(DATAFRAME["A"], bins=7)
  
  # After
  HIST_BINS = 7  # "Optimal for dataset distribution"
  ax.hist(df["A"], bins=HIST_BINS)
  ```
- **Best Practice**: Replace magic numbers with named constants.  

---

### Summary of Critical Fixes  
| Priority | Issue Type                | Key Action                                  |
|----------|---------------------------|---------------------------------------------|
| High     | Global State              | Replace globals with parameters/return values |
| High     | Single Responsibility     | Split functions by task (e.g., stats vs. I/O) |
| Medium   | Documentation             | Add docstrings for all public functions     |
| Low      | Redundant Operations      | Remove duplicate calculations               |

**Prevention Principle**: Favor **explicit dependencies** over global state and **document intent** over implementation details. This ensures testability, clarity, and maintainability.