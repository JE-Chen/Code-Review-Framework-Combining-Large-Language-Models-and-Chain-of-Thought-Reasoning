### Code Review

#### Naming Conventions
* **`fn_processTransactions`**: Use `snake_case` for Python functions (e.g., `process_transactions`) and avoid Hungarian notation prefixes like `fn_`.
* **`lst_transactions`**: Avoid type-prefixes like `lst_`. Use descriptive names like `transactions`.
* **`check(x)`**: The name is too vague. Rename to something descriptive like `is_large_transaction`.

#### Logic & Correctness
* **`Analyzer.analyze`**: If the `values` list is empty (e.g., all inputs were `0.0`), `statistics.mean`, `statistics.median`, and `max()` will raise errors (e.g., `StatisticsError` or `ValueError`). Add a check for an empty list.
* **`calculate_stats`**: This function will crash with an `IndexError` if `numbers` is an empty list when accessing `temp[0]` and `temp[-1]`.
* **`TransactionStore.records`**: Defined as a class attribute. This means all instances of `TransactionStore` share the same list of records, which is likely a bug if multiple stores are intended. Move it to `__init__`.

#### Software Engineering Standards
* **`calculate_stats`**: The loop to copy `numbers` into `temp` is redundant. Use `sorted(numbers)` to create a sorted copy in one line.
* **`format_transaction`**: Use f-strings for better readability and performance instead of string concatenation with `+`.
* **`Analyzer`**: The `analyze` method uses a series of `if` statements and defaults to `mean`. Consider using a dictionary mapping or a more explicit error for unsupported modes.

#### Readability & Consistency
* **`check(x)`**: The function can be simplified to a single line: `return x > 100`.
* **`fn_processTransactions`**: The logic for `last_user` is slightly redundant. Initializing `last_user` to the first element's user or using a more idiomatic grouping method (like `itertools.groupby`) would be cleaner.