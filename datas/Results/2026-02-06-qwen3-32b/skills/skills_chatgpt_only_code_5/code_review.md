### Diff #1

---

### **Summary**
This diff introduces a transaction processing pipeline that groups transactions by user, computes statistics on grouped totals, formats individual transactions, and prints results. Key components include:
- `fn_processTransactions`: Groups transactions by user and returns per-user totals.
- `Analyzer`: Computes statistical measures (mean, median, max) on numeric data.
- `TransactionStore`/`TransactionService`: Manages transaction storage and retrieval.
- `format_transaction`: Formats transactions with "BIG" or "SMALL" labels.
- `print_and_collect`: Prints formatted transactions and collects line lengths.
- `calculate_stats`/`report`: Computes and displays min/max/avg statistics.

Non-expert explanation:  
The code processes a list of transactions (user, amount, date), groups them by user, computes the total per user, analyzes those totals (e.g., average), and prints each transaction with a size label ("BIG" if amount > 100). It also computes statistics on the printed line lengths.

---

### **Linting Issues**
| File/Line | Violation | Correction |
|-----------|-----------|------------|
| `fn_processTransactions` (line 10) | Unnecessary `fn_` prefix in function name | Rename to `process_transactions` |
| `lst_transactions` (line 10) | Prefix `lst_` for parameter (non-standard) | Rename to `transactions` |
| `check` (line 92) | Generic name (`check`) with unclear purpose | Rename to `is_big_amount` |
| `format_transaction` (lines 97-98) | String concatenation (`+`) instead of f-strings | Use f-string: `f"{tx['user']} | {date} | {tx['amount']} | {label}"` |
| `calculate_stats` (line 114) | Unnecessary `temp` variable (could use `sorted`) | Replace with `sorted_numbers = sorted(numbers)` |

---

### **Code Smells**
| Location | Issue | Why Problematic | Recommendation |
|----------|-------|-----------------|----------------|
| `print_and_collect` (lines 101-107) | Mixed responsibility: Prints to console AND returns data | Makes unit testing impossible (can’t isolate printing logic) and prevents reuse | Split into `format_transactions` (returns formatted list) and `print_transactions` (handles I/O) |
| `TransactionStore.records` (line 64) | Class-level mutable state shared across instances | Creates hidden coupling; multiple `TransactionStore` instances would share data | Replace with instance-level `self.records = []` |
| `Analyzer.analyze` (lines 44-55) | Unvalidated `mode` parameter; returns mean on invalid input | Silent failure if invalid mode passed (e.g., `mode="invalid"`); violates single responsibility | Add mode validation: `if mode not in ["mean", "median", "max"]: raise ValueError` |
| `check` (line 92) | Hardcoded threshold `100` | Violates DRY; if threshold changes, multiple places must update | Define as constant: `BIG_AMOUNT_THRESHOLD = 100` |
| `calculate_stats` (lines 110-120) | Sorts input list (O(n log n)) when min/max can be computed in O(n) | Inefficient for large lists; unnecessary sorting | Compute min/max directly: `min_val = min(numbers); max_val = max(numbers)` |
| `main` (lines 125-143) | Hardcoded transaction data and logic | Limits flexibility; prevents external data sources | Accept data via `sys.argv` or config; move transaction setup to separate function |