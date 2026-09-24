### Code Review

#### Naming Conventions
*   **`fn_processTransactions`**: Non-standard naming. Use `snake_case` (e.g., `process_transactions`) to follow Python conventions.
*   **`lst_transactions`**: Avoid encoding types in names (Hungarian notation). Use `transactions`.
*   **`check(x)`**: Vague name. Use something descriptive like `is_large_transaction`.
*   **`temp`**: Generic name in `calculate_stats`. Use `sorted_numbers`.

#### Logic & Correctness
*   **`Analyzer.analyze`**: If the `values` list is empty (e.g., all inputs were `0.0`), `statistics.mean`, `statistics.median`, and `max()` will raise `StatisticsError` or `ValueError`. Add a check for an empty list.
*   **`calculate_stats`**: Will raise an `IndexError` or `ZeroDivisionError` if `numbers` is an empty list.

#### Software Engineering Standards
*   **`TransactionStore.records`**: This is a class-level attribute (shared mutable state). If multiple `TransactionStore` instances are created, they will all share and mutate the same list, leading to unpredictable behavior. Move `records = []` into `__init__`.
*   **`Analyzer.analyze`**: The method returns `statistics.mean(values)` as a fallback if the `mode` is unrecognized. This is an implicit behavior that could mislead the caller. Raise a `ValueError` for unsupported modes.
*   **`calculate_stats`**: The manual loop to copy the list into `temp` is redundant. Use `sorted(numbers)`.

#### Readability & Consistency
*   **`format_transaction`**: String concatenation using `+` is less readable and less efficient than f-strings.
*   **`check(x)`**: The `if/else` returning boolean is redundant. Use `return x > 100`.

#### Performance & Security
*   **`print_and_collect`**: This function violates the Single Responsibility Principle by mixing I/O (`print`) with data processing (`collected.append`). Split these into two functions.