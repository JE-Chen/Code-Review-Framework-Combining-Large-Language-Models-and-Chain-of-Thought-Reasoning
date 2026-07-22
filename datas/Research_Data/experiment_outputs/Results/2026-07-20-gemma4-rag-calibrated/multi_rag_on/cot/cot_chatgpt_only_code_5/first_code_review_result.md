### Code Review

**Naming Conventions**
* `fn_processTransactions`: Use `snake_case` for Python functions (e.g., `process_transactions`). The `fn_` prefix is redundant.
* `check(x)`: The name is too vague. Rename to `is_large_transaction` or `is_big_amount` to describe its purpose.
* `temp` in `calculate_stats`: Use a more descriptive name like `sorted_numbers`.

**Software Engineering Standards**
* `TransactionStore.records`: The `records` list is defined as a class attribute, making it a global singleton. This will cause data to persist across different instances of `TransactionStore`. Move it to `__init__` as `self.records`.
* `Analyzer.analyze`: The method uses a series of `if` statements and defaults to `mean` if an invalid mode is passed. Consider raising a `ValueError` for unsupported modes to avoid silent failures.
* `calculate_stats`: The loop used to copy `numbers` into `temp` is unnecessary; use `sorted(numbers)` to create a new sorted list in one line.

**Logic & Correctness**
* `calculate_stats`: The function will crash with an `IndexError` or `ZeroDivisionError` if `numbers` is an empty list. Add a check for empty input.
* `Analyzer.analyze`: The logic filters out `0.0` values. If a transaction total is legitimately `0.0`, it is excluded from the mean/median/max, which may lead to incorrect statistical results.

**Readability & Consistency**
* `format_transaction`: Use f-strings (e.g., `f"{tx['user']} | {date}..."`) instead of string concatenation for better readability and performance.
* `calculate_stats`: The `+ 0.0` in the average calculation is redundant in Python 3, as division already returns a float.

**Performance & Security**
* `TransactionStore`: Since `records` is a class variable, it creates a memory leak if the application runs for a long time and stores many transactions across different store instances.