### Code Review

**Logic & Correctness**
* **Redundant Parameter:** In `create_order`, `total_price` is passed as an argument but is immediately overwritten by the calculation in `process_order`. This creates confusion about the source of truth for the order total.
* **Inconsistent Logger Interface:** `log_order` uses `hasattr` to check for `log` vs `write`. This violates the Interface Segregation/Liskov Substitution principles. Loggers should share a consistent method name (e.g., `log`).

**Software Engineering Standards**
* **Data Structure:** Using dictionaries for `order` makes the code prone to `KeyError` and lacks type safety. Consider using a `dataclass` or `NamedTuple`.
* **Modularity:** `process_order` handles too many responsibilities (validation, price calculation, and logging/printing). The calculation logic should be separated from the order state update.
* **Hardcoded Values:** Discount rates and thresholds in `calculate_discount` are hardcoded. These should be moved to a configuration object or constants for easier maintenance.

**Readability & Naming**
* **Naming:** `now` in `process_order` is acceptable, but `current_time` would be more descriptive.
* **Formatting:** The code is generally well-formatted and follows standard indentation.

**Suggestions for Improvement**
* **Unify Logger API:** Rename `ConsoleLogger.write` to `log` to remove the conditional checks in `log_order`.
* **Refactor Order to Class:** Convert the order dictionary to a class to ensure all required fields (like `final_price`) are explicitly defined.
* **Simplify `calculate_discount`:** Use a mapping (dictionary) for customer types to reduce the nested `if/elif` blocks.