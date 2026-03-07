### Diff #1
**File:** `data_analysis.py`

---

### **Summary**
- **Purpose & Scope**: This new file implements a basic data analysis workflow for a sample dataset. It creates a DataFrame, adds random columns, calculates average age with conditional messaging, and prints descriptive statistics. The code is intended for demonstration but lacks modularity.
- **Affected Components**: 
  - Global variables (`GLOBAL_DF`, `ANOTHER_GLOBAL`)
  - Single monolithic function (`functionThatDoesTooMuchAndIsNotClear`)
  - Main execution block
- **Plain-Language Explanation**:  
  *This code generates fake student data, adds random scores, checks if the average age is reasonable, and shows summary stats. It’s like a "quick demo" but mixes too many tasks into one function.*

---

### **Linting Issues**
- **Poor Naming Conventions**  
  - `functionThatDoesTooMuchAndIsNotClear`: Overly long, negative, and implementation-focused (not intent-driven).  
  - `GLOBAL_DF`, `ANOTHER_GLOBAL`: Use of `GLOBAL_` prefix is redundant and error-prone.  
  *Suggestion: Rename to `create_sample_data`, `ANALYSIS_START_MESSAGE` (avoiding `GLOBAL` entirely).*

- **Magic Numbers**  
  - `random.randint(0, 10)` uses unexplained values.  
  *Suggestion: Replace with named constants like `RANDOM_SCORE_RANGE = (0, 10)`.*

- **Inconsistent String Handling**  
  - Mixed Chinese/English in print statements (`"平均年齡在合理範圍:"` vs. English error messages).  
  *Suggestion: Use consistent language (e.g., English for code, add comments for non-English text).*

---

### **Code Smells**
- **Single Function with Multiple Responsibilities**  
  - *Problem*: The function creates data, manipulates columns, handles errors, and prints results.  
  - *Why*: Hard to test, debug, or reuse. Changes in one area (e.g., error handling) risk breaking unrelated logic.  
  - *Fix*: Split into:  
    ```python
    def create_sample_data() -> pd.DataFrame: ...
    def add_random_score_columns(df: pd.DataFrame) -> pd.DataFrame: ...
    def validate_age_mean(df: pd.DataFrame) -> str: ...
    ```

- **Global State Abuse**  
  - *Problem*: `GLOBAL_DF` and `ANOTHER_GLOBAL` are mutable globals.  
  - *Why*: Causes hidden dependencies, prevents parallel execution, and violates encapsulation.  
  - *Fix*: Pass data as function parameters instead of relying on globals.

- **Overly Broad Exception Handling**  
  - *Problem*: `except Exception as e` catches *all* errors (e.g., `KeyError` from missing columns).  
  - *Why*: Masks bugs and makes debugging impossible.  
  - *Fix*: Handle specific exceptions (e.g., `ValueError` for invalid data).

- **Hardcoded Data & Logic**  
  - *Problem*: Sample data (`Name`, `Age`, `Score`) is hardcoded inside the function.  
  - *Why*: Prevents reusability for different datasets.  
  - *Fix*: Accept input parameters (e.g., `data: dict`) or load from a source (e.g., CSV).

---

### **Key Refactoring Recommendations**
1. **Eliminate globals** → Pass data via function parameters.  
2. **Split monolithic function** → Break into focused, testable units.  
3. **Replace magic numbers** → Use descriptive constants.  
4. **Improve error handling** → Catch specific exceptions.  
5. **Externalize sample data** → Load from config or file.  

*Example of improved structure:*  
```python
# data_analysis.py
import pandas as pd
import random

ANALYSIS_START_MESSAGE = "分析開始"

def create_sample_dataframe() -> pd.DataFrame:
    return pd.DataFrame({
        "Name": ["Alice", "Bob", "Charlie", "David", "Eve"],
        "Age": [25, 30, 35, 40, 45],
        "Score": [88, 92, 95, 70, 60]
    })

def add_random_score_column(df: pd.DataFrame) -> pd.DataFrame:
    random_offset = random.randint(0, 10)
    df["ScorePlusRandom"] = df["Score"] + random_offset
    return df

def validate_average_age(df: pd.DataFrame) -> str:
    mean_age = df["Age"].mean()
    if mean_age < 20:
        return f"平均年齡過低: {mean_age}"
    if mean_age > 50:
        return f"平均年齡過高: {mean_age}"
    return f"平均年齡在合理範圍: {mean_age}"

def main():
    print(ANALYSIS_START_MESSAGE)
    df = create_sample_dataframe()
    df = add_random_score_column(df)
    print(validate_average_age(df))
    print(df.describe())
    
if __name__ == "__main__":
    main()
```