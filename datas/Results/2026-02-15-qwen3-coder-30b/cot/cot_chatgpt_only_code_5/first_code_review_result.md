### Code Review Summary

#### ✅ **Readability & Consistency**
- Indentation and formatting are consistent but could benefit from stricter PEP 8 adherence.
- Comments are missing; adding inline comments would improve understanding of logic flow.

#### ✅ **Naming Conventions**
- Function/class names like `fn_processTransactions`, `check`, and `format_transaction` lack clarity.
- Variables such as `x`, `tx`, `temp`, and `n` do not clearly express their purpose.

#### ✅ **Software Engineering Standards**
- Functions perform multiple responsibilities (e.g., `print_and_collect` does printing and data collection).
- Duplicated code exists in `calculate_stats` and repeated use of list copying.

#### ⚠️ **Logic & Correctness**
- Potential division-by-zero error in `calculate_stats` if input list is empty.
- No handling of invalid transaction entries in `fn_processTransactions`.

#### ⚠️ **Performance & Security**
- Global state via `TransactionStore.records` can cause concurrency issues and test instability.
- Inefficient sorting in `calculate_stats`.

#### ⚠️ **Documentation & Testing**
- No docstrings or type hints provided.
- Unit tests are not included; critical logic lacks coverage.

---

### Suggestions for Improvement

- Rename functions like `fn_processTransactions` → `group_transaction_totals`.
- Replace generic variable names (`x`, `n`) with descriptive ones.
- Separate concerns: e.g., move output logic out of `print_and_collect`.
- Add defensive checks for edge cases (empty inputs).
- Use local variables instead of global `TransactionStore.records`.
- Consider using `statistics.fmean()` or `statistics.fmedian()` for better floating-point handling.

---

### Example Refactor

```python
def group_transaction_totals(transactions):
    """Group transactions by user and compute total amounts."""
    ...
```

This improves clarity and aligns with the principle that functions should have one clear responsibility.