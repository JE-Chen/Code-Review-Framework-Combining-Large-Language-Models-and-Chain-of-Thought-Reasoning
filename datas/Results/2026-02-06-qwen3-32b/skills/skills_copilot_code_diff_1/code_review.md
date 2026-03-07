### Diff #1

#### **Summary**
- **Purpose**: Introduces a new Flask web application for generating random numbers and computing basic statistics (mean, median). Provides endpoints to generate data, analyze it, and reset state.
- **Affected Files**: `app.py` (new file).
- **Plain Explanation**: This app lets users generate a list of random numbers (up to 37), see averages and medians of those numbers, and clear the data. All state is stored globally (not recommended for production).

---

#### **Linting Issues**
- **Violations**:
  - ❌ `meanVal` uses camelCase (should be snake_case).  
    *Line 25: `meanVal = statistics.mean(DATA)`*
  - ❌ `LIMIT` is a magic number (37) without context.  
    *Line 10: `LIMIT = 37`*
  - ❌ `medianPlus42` uses a magic number (42) without explanation.  
    *Line 33: `RESULTS["medianPlus42"] = statistics.median(DATA) + 42`*
  - ❌ Global variables (`DATA`, `RESULTS`) are declared without docstrings.  
    *Lines 7–8: `DATA = []`, `RESULTS = {}`*
- **Corrections**:
  ```python
  # Replace camelCase
  mean_value = statistics.mean(DATA)  # Not meanVal

  # Replace magic numbers
  MAX_DATA_SIZE = 37
  MEDIAN_ADJUSTMENT = 42
  ```

---

#### **Code Smells**
- **Global State Abuse** (Critical):  
  Uses `global DATA, RESULTS` everywhere. Makes code non-testable, prone to race conditions, and violates encapsulation.  
  *Why bad*: A single user’s `/analyze` call could corrupt another user’s data. *Fix*: Use request-specific state or dependency injection.
  
- **Redundant Computation** (High):  
  Computes `statistics.mean(DATA)` twice in `analyze()`.  
  *Why bad*: Wastes CPU cycles. *Fix*: Store result in a variable:  
  ```python
  mean_val = statistics.mean(DATA)
  RESULTS["mean"] = mean_val
  RESULTS["meanAgain"] = mean_val  # Remove duplicate call
  ```

- **Confusing Naming** (Medium):  
  `meanAgain` and `medianPlus42` imply purposeless duplication.  
  *Why bad*: Misleads maintainers. *Fix*: Rename to `mean` and `median_adjusted` (with context).

- **Arbitrary Conditions** (Medium):  
  Hardcoded thresholds (`len(DATA) > 5`, `>10`).  
  *Why bad*: No rationale for thresholds. *Fix*: Parameterize or remove logic.

- **Missing Validation** (Low):  
  `/analyze` returns `RESULTS` even when empty.  
  *Why bad*: Could expose uninitialized state. *Fix*: Return `{}` instead of `RESULTS` when empty.