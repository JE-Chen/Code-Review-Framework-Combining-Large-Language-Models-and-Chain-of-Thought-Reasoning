### Code Review

**Naming Conventions**
* **`fn_processTransactions`**: Non-standard naming. Use `snake_case` (e.g., `process_transactions`) to follow PEP 8.
* **`check(x)`**: Vague name. Rename to something descriptive like `is_large_transaction`.
* **`temp`**: Generic name in `calculate_stats`. Use `sorted_numbers` or similar.

**Logic & Correctness**
* **`Analyzer.analyze`**: Potential `StatisticsError` or `ValueError` if `values` is empty (e.g., if all inputs are `0.0`). Add a check for an empty list.
* **`calculate_stats`**: Potential `IndexError` and `ZeroDivisionError` if `numbers` is an empty list.
* **`TransactionStore.records`**: Defined as a class attribute. This means all instances of `TransactionStore` share the same list, which will cause data leakage between different store instances. Move it to `__init__`.

**Software Engineering Standards**
* **`calculate_stats`**: The loop to copy `numbers` into `temp` is redundant. Use `sorted(numbers)` to create a new sorted list in one line.
* **`format_transaction`**: String concatenation using `+` is less efficient and harder to read than f-strings.
* **`Analyzer.analyze`**: The final `return statistics.mean(values)` acts as a default for any unknown mode. It is better to raise a `ValueError` for unsupported modes to avoid silent logic errors.

**Readability & Consistency**
* **`format_transaction`**: Hardcoded date `"2026-01-01"` as a default is a "magic value"; consider using a constant or a proper date utility.
* **`check` function**: Can be simplified to a single line: `return x > 100`.