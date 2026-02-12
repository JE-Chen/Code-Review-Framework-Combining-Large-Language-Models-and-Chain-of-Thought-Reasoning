### Title: Monolithic Data Analysis Function with Global State and Poor Design

### Overview
This code creates a hardcoded sample dataset, adds non-deterministic random columns, analyzes age statistics, and prints results. It suffers from global state pollution, ambiguous naming, lack of modularity, and weak error handling. The function does *everything* without separation of concerns.

---

### Detailed Explanation

#### Core Components
| Name                          | Purpose                                                                 | Critical Flaws                                                                 |
|-------------------------------|-------------------------------------------------------------------------|-------------------------------------------------------------------------------|
| `GLOBAL_DF`                   | Global DataFrame holding sample data                                    | Causes hidden dependencies and state leaks                                     |
| `ANOTHER_GLOBAL`              | Hardcoded string for startup message                                    | Poorly named, no context                                                       |
| `functionThatDoesTooMuchAndIsNotClear()` | Single function handling data creation, transformation, analysis, and output | Violates single responsibility principle; no input/output contracts |

#### Step-by-Step Flow
1. **Data Creation**  
   Hardcoded 5-row dataset for `Name`, `Age`, `Score` is created and assigned to global `GLOBAL_DF`.

2. **Non-Deterministic Transformation**  
   Adds two columns (`ScorePlusRandom`, `ScorePlusRandomAgain`) by adding *different random integers (0-10)* to each row.  
   → *Problem: Results vary per run, making analysis non-reproducible.*

3. **Age Analysis**  
   Calculates mean age and prints:
   - "平均年齡在合理範圍" if 20 < mean < 50
   - "平均年齡過高" if mean ≥ 50
   - "平均年齡過低" if mean ≤ 20  
   → *Problem: Logic is inverted (checks `mean > 20` then `mean < 50` but prints "合理" for mean < 50)*

4. **Statistical Output**  
   Prints `describe()` summary of the DataFrame.

5. **Execution**  
   Prints `ANOTHER_GLOBAL` ("分析開始"), then triggers the monolithic function.

---

### Key Issues

#### 1. Global State Corruption
- **Problem**: `GLOBAL_DF` is mutated by the function and accessed globally.  
- **Impact**:  
  - Breaks testability (can't isolate logic)  
  - Causes hidden failures if multiple functions modify it  
  - *Example:* If another function overwrites `GLOBAL_DF`, the analysis becomes invalid.

#### 2. Ambiguous Naming
- `functionThatDoesTooMuchAndIsNotClear()`:  
  - Describes *what it avoids* (clear code), not *what it does*.  
  - Violates naming principle: *Names should reflect intent, not implementation*.  
- `ANOTHER_GLOBAL`:  
  - No context (why "another"? Why global?).  
  - *Better:* `STARTUP_MESSAGE = "Starting data analysis..."`

#### 3. Poor Error Handling
```python
try: ... except Exception as e:
    print("我不管錯誤是什麼:", e)  # Ignores all errors
```
- **Impact**: Silently discards critical failures (e.g., missing `Age` column).

#### 4. Hardcoded Data
- Dataset is fixed to 5 rows.  
- *No way to analyze real data or different samples.*

#### 5. Non-Determinism
- Random numbers in `ScorePlusRandom*` make results unpredictable.  
- *Critical for reproducibility in analysis.*

---

### Edge Cases & Errors
| Scenario                     | Original Behavior       | Improved Approach |
|------------------------------|-------------------------|-------------------|
| Missing `Age` column         | Crashes silently        | Validate input before analysis |
| Dataset size changes (e.g., 10 rows) | Fails silently        | Parameterize dataset size |
| Random seed not set          | Results vary per run    | Seed for reproducibility |
| Multiple analysis runs       | Global state corrupts   | Stateless functions |

---

### Performance & Security
- **Performance**: N/A (small hardcoded dataset).  
- **Security**: None directly, but global state could allow unintended data exposure in larger systems.

---

### Improvements

1. **Eliminate Global State**  
   ```python
   # BEFORE: GLOBAL_DF = pd.DataFrame(...)
   # AFTER: 
   def create_sample_data() -> pd.DataFrame:
       return pd.DataFrame({
           "Name": ["Alice", "Bob", ...],
           "Age": [25, 30, ...],
           "Score": [88, 92, ...]
       })
   ```
   *Why:* Functions become pure, testable, and reusable.

2. **Split Responsibilities**  
   ```python
   # BEFORE: One function doing everything
   # AFTER:
   def add_random_offsets(df: pd.DataFrame) -> pd.DataFrame:
       return df.assign(
           ScorePlusRandom=df["Score"] + random.randint(0, 10),
           ScorePlusRandomAgain=df["Score"] + random.randint(0, 10)
       )
   
   def analyze_age(df: pd.DataFrame) -> str:
       mean_age = df["Age"].mean()
       if mean_age > 50: 
           return "平均年齡過高"
       elif mean_age < 20: 
           return "平均年齡過低"
       return "平均年齡在合理範圍"
   ```
   *Why:* Each function has one clear purpose.

3. **Fix Logic & Naming**  
   - Rename `functionThatDoesTooMuch...` → `analyze_sample_dataset`  
   - Correct age analysis logic (fix inverted conditions)  
   - *Rationale:* Clarity prevents bugs.

4. **Add Input Validation**  
   ```python
   def analyze_age(df: pd.DataFrame) -> str:
       if "Age" not in df.columns:
           raise ValueError("DataFrame missing 'Age' column")
   ```
   *Why:* Fail fast with clear errors instead of silent crashes.

5. **Make Randomness Deterministic**  
   ```python
   def add_random_offsets(df: pd.DataFrame, seed: int = 42) -> pd.DataFrame:
       random.seed(seed)
       # ...
   ```
   *Why:* Reproducible results for analysis.

---

### Example Usage (Improved)
```python
import pandas as pd
import random

def create_sample_data() -> pd.DataFrame:
    return pd.DataFrame({
        "Name": ["Alice", "Bob", "Charlie", "David", "Eve"],
        "Age": [25, 30, 35, 40, 45],
        "Score": [88, 92, 95, 70, 60]
    })

def add_random_offsets(df: pd.DataFrame, seed: int = 42) -> pd.DataFrame:
    random.seed(seed)
    return df.assign(
        ScorePlusRandom=df["Score"] + random.randint(0, 10),
        ScorePlusRandomAgain=df["Score"] + random.randint(0, 10)
    )

def analyze_age(df: pd.DataFrame) -> str:
    if "Age" not in df.columns:
        raise ValueError("Missing 'Age' column")
    mean_age = df["Age"].mean()
    if mean_age > 50:
        return "平均年齡過高"
    if mean_age < 20:
        return "平均年齡過低"
    return "平均年齡在合理範圍"

def main():
    print("Starting data analysis...")
    df = create_sample_data()
    df = add_random_offsets(df, seed=42)
    print(analyze_age(df))
    print("\nDescriptive Statistics:")
    print(df.describe())

if __name__ == "__main__":
    main()
```

---

### Why This Matters
- **Readability**: Names and structure immediately convey intent.  
- **Maintainability**: Fixing age logic only requires changing one function.  
- **Testability**: Functions can be tested in isolation (e.g., `test_analyze_age()`).  
- **Reliability**: Input validation and deterministic randomness prevent silent failures.  
- **Scalability**: Handles arbitrary datasets (not hardcoded samples).  

> 💡 **Golden Rule**: *If a function does more than one thing, split it. If a variable is global, make it an input.* This code violates both.