### Code Smell Type: Global Variables  
**Problem Location**:  
```python
GLOBAL_DF = None
ANOTHER_GLOBAL = "分析開始"
# ... later in function
global GLOBAL_DF
```  
**Detailed Explanation**:  
Global variables (`GLOBAL_DF`, `ANOTHER_GLOBAL`) create hidden dependencies and state coupling. They violate encapsulation, making the code harder to test, reason about, and maintain. Changes to `GLOBAL_DF` anywhere in the codebase can cause unexpected side effects. The use of `global` in `functionThatDoesTooMuchAndIsNotClear` further complicates state management. This is a critical violation of software engineering best practices.  

**Improvement Suggestions**:  
1. Replace `GLOBAL_DF` with function parameters/return values.  
2. Remove `ANOTHER_GLOBAL` as a global; pass strings via arguments or use constants in a dedicated config module.  
3. Refactor to eliminate global state entirely. Example:  
   ```python
   def create_sample_dataframe() -> pd.DataFrame:
       return pd.DataFrame({
           "Name": ["Alice", "Bob", ...],
           "Age": [25, 30, ...],
           "Score": [88, 92, ...]
       })
   ```  
**Priority Level**: High  

---

### Code Smell Type: Function with Multiple Responsibilities (Violates SRP)  
**Problem Location**:  
```python
def functionThatDoesTooMuchAndIsNotClear():
    # Creates DataFrame
    # Adds columns
    # Calculates mean
    # Prints results
    # ... (entire function body)
```  
**Detailed Explanation**:  
This function handles data creation, transformation, business logic, and output. It violates the Single Responsibility Principle (SRP), making it:  
- Long (25 lines) and hard to read.  
- Impossible to test in isolation (requires global state).  
- Prone to bugs when modifying one part.  
For example, adding a new column would require changes in the same function, risking regressions.  

**Improvement Suggestions**:  
Split into focused functions:  
```python
def create_sample_dataframe() -> pd.DataFrame: ...  # Data creation
def add_random_columns(df: pd.DataFrame) -> pd.DataFrame: ...  # Transformation
def validate_age_mean(mean: float) -> str: ...  # Business logic
def generate_report(df: pd.DataFrame) -> str: ...  # Output
```  
**Priority Level**: High  

---

### Code Smell Type: Poor Naming Conventions  
**Problem Location**:  
```python
functionThatDoesTooMuchAndIsNotClear()  # Unintentionally negative
ANOTHER_GLOBAL = "分析開始"  # Vague
GLOBAL_DF  # Ambiguous
```  
**Detailed Explanation**:  
- Function name describes *what it isn't* instead of *what it does*.  
- `ANOTHER_GLOBAL` is non-descriptive (what is "another"?) and inconsistent with `GLOBAL_DF`'s naming pattern.  
- `GLOBAL_DF` implies global state, which is already problematic.  
Poor names increase cognitive load and reduce code readability.  

**Improvement Suggestions**:  
- Rename function to `analyze_sample_data` (after splitting logic).  
- Replace `ANOTHER_GLOBAL` with `START_MESSAGE = "分析開始"`.  
- Use `sample_df` instead of `GLOBAL_DF` (if temporary).  
**Priority Level**: Medium  

---

### Code Smell Type: Overly Broad Exception Handling  
**Problem Location**:  
```python
try:
    ...
except Exception as e:
    print("我不管錯誤是什麼:", e)  # Catch-all
```  
**Detailed Explanation**:  
Catching `Exception` hides all errors (e.g., `KeyError`, `TypeError`), masking bugs and making debugging impossible. The message "我不管錯誤是什麼" ("I don’t care what the error is") demonstrates fatal negligence. This violates defensive programming standards.  

**Improvement Suggestions**:  
1. Catch specific exceptions (e.g., `ValueError` for empty columns).  
2. Add meaningful logging:  
   ```python
   except ValueError as e:
       logging.error("Age column empty: %s", e)
       raise  # Re-raise after logging
   ```  
**Priority Level**: High  

---

### Code Smell Type: Magic Numbers  
**Problem Location**:  
```python
GLOBAL_DF["ScorePlusRandom"] = GLOBAL_DF["Score"] + random.randint(0, 10)
```  
**Detailed Explanation**:  
`0` and `10` are arbitrary without context. Future maintainers won’t know:  
- Why the range is `[0, 10]`?  
- If this value should change.  
This violates the "meaningful constants" principle.  

**Improvement Suggestions**:  
Define constants:  
```python
MAX_RANDOM_SCORE = 10
RANDOM_SCORE_RANGE = (0, MAX_RANDOM_SCORE)
# Then: random.randint(*RANDOM_SCORE_RANGE)
```  
**Priority Level**: Low  

---

### Code Smell Type: Hardcoded Data  
**Problem Location**:  
```python
data = {
    "Name": ["Alice", "Bob", ...],
    "Age": [25, 30, ...],
    "Score": [88, 92, ...]
}
```  
**Detailed Explanation**:  
Sample data is hardcoded. This prevents reuse and forces code changes for data updates. In production, data should come from external sources (e.g., files, APIs).  

**Improvement Suggestions**:  
- Parameterize data source:  
  ```python
  def load_sample_data(path: str = "sample.csv") -> pd.DataFrame:
      return pd.read_csv(path)
  ```  
**Priority Level**: Medium  

---

### Code Smell Type: Missing Documentation  
**Problem Location**:  
No docstrings for `functionThatDoesTooMuchAndIsNotClear()`.  
**Detailed Explanation**:  
Lack of documentation makes the function’s purpose, inputs, and outputs unclear. This impedes onboarding and maintenance.  

**Improvement Suggestions**:  
Add a docstring:  
```python
def analyze_sample_data() -> None:
    """Processes sample data to compute age statistics and score distributions.
    Prints mean age validation and descriptive statistics.
    """
```  
**Priority Level**: Low