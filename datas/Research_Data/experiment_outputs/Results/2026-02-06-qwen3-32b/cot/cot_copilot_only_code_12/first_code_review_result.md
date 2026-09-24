- **Naming Conventions**:  
  Rename `resultList` → `result_list` and `tempStorage` → `temp_storage` to follow Python snake_case conventions.  
  Rename `calcStats` → `compute_column_stats` for clearer semantic meaning.

- **Global Variables**:  
  Avoid global state (`DATAFRAME`, `resultList`, `temp_storage`). Pass data as function parameters instead to improve testability and reduce side effects.

- **Redundant Logic**:  
  `calcStats` recalculates mean for column "A" twice (e.g., `meanA` and `meanA_again`), causing unnecessary computation. Remove the redundant second calculation.

- **Hardcoded Behavior**:  
  `plotData` is hardcoded to plot only column "A" without flexibility. Add a parameter for the column name to support future reuse.

- **Inconsistent Storage**:  
  `tempStorage` is updated for "A"/"B" but not for other columns, while `resultList` handles all columns. Ensure consistent storage patterns across logic branches.