Here's the concise code review focusing on the most obvious issues:

- **Redundant `paid` initialization**:  
  `create_order` sets `paid=False`, but `process_order` resets it to `False` again. Remove the redundant assignment in `process_order`.

- **Discount logic boundary issue**:  
  `calculate_discount` uses `>` instead of `>=` for thresholds (e.g., `total > 1000` for 20% discount). This means orders exactly at $1000 won't get the higher discount. Verify if business rules require `>=`.

- **Over-commented code**:  
  Remove redundant comments like `# list of (name, price)` – variable names and structure should be self-explanatory.

- **Missing docstrings**:  
  Functions lack docstrings explaining purpose, parameters, and return values. Add minimal documentation for clarity.

- **Inconsistent total calculation**:  
  `create_order` expects caller to pass `total_price=0`, but `process_order` recalculates it. Consider making `total_price` optional and derived only in `process_order`.

- **Unnecessary `verbose` handling**:  
  The `verbose` parameter in `process_order` prints directly to console. Prefer logging for testability and flexibility.

- **Type validation missing**:  
  `items` expects tuples of `(str, float)`, but no validation exists. Add error handling for invalid item formats.