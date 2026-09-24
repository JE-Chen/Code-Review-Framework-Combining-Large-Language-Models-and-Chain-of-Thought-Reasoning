### Pull Request Summary

**Key Changes**
- Implemented a transaction processing system including storage, service layers, and analysis utilities.
- Added functionality to group transaction totals by user, calculate statistical metrics (mean, median, max), and generate a formatted report.

**Impact Scope**
- New implementation of `TransactionStore`, `TransactionService`, `Analyzer`, and several utility functions for data processing and reporting.

**Purpose of Changes**
- Establish a baseline for processing and analyzing user transaction data.

**Risks and Considerations**
- The current implementation relies on a shared class-level list for storage, which will cause data persistence across different instances of `TransactionStore`.
- Lack of input validation on transaction dictionaries may lead to `KeyError` if expected keys are missing.

**Items to Confirm**
- Verify if `TransactionStore.records` should be an instance attribute rather than a class attribute.
- Confirm the expected behavior of `Analyzer.analyze` when an unsupported mode is passed (currently defaults to "mean").

---

### Code Review

#### 1. Readability & Consistency
- **Naming Conventions**: 
    - `fn_processTransactions` uses a mix of prefixing (`fn_`) and camelCase, which violates PEP 8 (should be `process_transactions`).
    - `lst_transactions` uses Hungarian notation (`lst_`), which is generally discouraged in Python.
- **Formatting**: The code is generally well-indented, but some logic is overly verbose (e.g., `calculate_stats` manually copying a list before sorting).

#### 2. Software Engineering Standards
- **Modularization**: The `Analyzer` class contains only a static method. This should likely be a standalone function unless more state/behavior is planned.
- **Redundancy**: In `calculate_stats`, the loop to copy `numbers` into `temp` is redundant; `sorted(numbers)` achieves the same result more concisely.

#### 3. Logic & Correctness
- **Boundary Conditions**: In `calculate_stats`, if `numbers` is an empty list, the code will raise an `IndexError` at `temp[0]` and a `ZeroDivisionError` at the average calculation.
- **Logic Bug**: In `fn_processTransactions`, the logic assumes transactions are pre-sorted by user. If users are interleaved (e.g., Alice, Bob, Alice), it will create multiple separate totals for Alice rather than one aggregate.

#### 4. Performance & Security
- **Input Validation**: `format_transaction` uses `tx["user"]` and `tx["amount"]` without checking if these keys exist, which will crash the program on malformed data.
- **Complexity**: The current logic is $O(N)$, which is appropriate for the task.

#### 5. RAG Rules Violations
- **Shared Mutable State**: `TransactionStore.records = []` is defined at the class level. This is a critical bug: every instance of `TransactionStore` will share the same list of records, leading to data leakage between different store instances.
- **Implicit Truthiness**: In `Analyzer.analyze`, `if x == 0.0: continue` is used. While explicit here, the logic effectively ignores zero-value transactions, which may be a business logic error.
- **Single Responsibility Principle**: `print_and_collect` performs two distinct tasks: printing to the console and calculating string lengths. These should be separated.
- **Magic Numbers**: The date `"2026-01-01"` in `format_transaction` is a hard-coded magic string.
- **Broad Return Types**: `Analyzer.analyze` returns a float/int, but the logic is fragile regarding the `mode` parameter.

#### 6. Documentation & Testing
- **Missing Tests**: There are no unit tests provided; only a `main()` execution block.
- **Documentation**: There are no docstrings explaining the expected input format for the transaction dictionaries.

### Final Score: ⚠️ Needs Work
The code is functional for a happy-path scenario but contains a significant architectural flaw regarding shared mutable state (`TransactionStore`) and lacks necessary error handling for empty datasets or missing dictionary keys.