### Diff #1

#### Summary
- **Purpose**: Generates random data, computes basic statistics (means for numeric columns), stores results, and plots a histogram.  
- **Affected files**: Single script handling data generation, analysis, and visualization.  
- **Plain explanation**: Creates fake data for columns A (integers), B (floats), and C (categorical). Calculates averages for A and B (redundantly), stores results in lists/dictionaries, and plots column A’s distribution. Finally prints all results.  

---

#### Linting Issues
- **Global variables**:  
  - `DATAFRAME`, `resultList`, and `tempStorage` are used globally without scope control (violates PEP8).  
  *Suggestion*: Replace with function parameters/return values.  
- **Magic numbers**:  
  - `bins=7` in `plotData()` lacks explanation.  
  *Suggestion*: Replace with `HIST_BINS = 7` or add a comment.  
- **Inconsistent naming**:  
  - `tempStorage` (camelCase) vs. `resultList` (snake_case).  
  *Suggestion*: Standardize to snake_case (e.g., `temp_storage`).  
- **Redundant imports**:  
  - `statistics as st` is unused outside `st.mean()`; direct import preferred.  
  *Suggestion*: Replace `import statistics as st` with `from statistics import mean`.  

---

#### Code Smells
- **Global state abuse**:  
  - Heavy reliance on globals (`DATAFRAME`, `resultList`, `tempStorage`) creates hidden dependencies and testability issues.  
  *Why problematic*: Breaks single-responsibility principle; hard to isolate logic.  
  *Refactor*: Pass DataFrame and storage as arguments to functions.  
- **Duplicate computation**:  
  - Mean for column "A" is calculated twice in `calcStats()` (`meanA` and `meanA_again`).  
  *Why problematic*: Wastes CPU cycles and confuses logic.  
  *Refactor*: Compute once and reuse.  
- **Hardcoded column names**:  
  - `calcStats()` checks explicit column names (`"A"`, `"B"`, `"C"`), breaking flexibility.  
  *Why problematic*: Fails if column names change; violates DRY.  
  *Refactor*: Accept column names as parameters or use type-based logic.  
- **Unused variable**:  
  - `tempStorage` is written to but never read (dead code).  
  *Why problematic*: Clutters code and suggests unclear design.  
  *Refactor*: Remove `tempStorage` entirely.  
- **Poor naming**:  
  - `tempStorage` implies temporary state but persists globally. `resultList` is vague.  
  *Why problematic*: Misleads maintainers about intent.  
  *Refactor*: Rename to `stats_store` (if kept) or eliminate.