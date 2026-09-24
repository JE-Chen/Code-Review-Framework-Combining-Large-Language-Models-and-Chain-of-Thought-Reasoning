### Code Review

**Logic & Correctness**
* **Redundant Parameter:** In `create_order`, `total_price` is passed as an argument but is immediately overwritten by the sum calculation in `process_order`. This creates confusion about the source of truth for the order total.
* **Inconsistent Logger Interface:** `FileLogger` uses `.log()` while `ConsoleLogger` uses `.write()`. This forces `log_order` to use `hasattr` checks, which is a fragile pattern.

**Software Engineering Standards**
* **Lack of Abstraction:** The `calculate_discount` function uses a deeply nested `if/elif` structure. This should be refactored into a mapping (dictionary) or a strategy pattern to improve maintainability as more customer types are added.
* **Interface Inconsistency:** `OrderPrinter`, `FileLogger`, and `ConsoleLogger` do not share a common base class or interface, hindering polymorphism.

**Readability & Naming**
* **Magic Numbers:** The discount rates (0.2, 0.1, 0.05, etc.) are hardcoded literals. These should be defined as named constants at the top of the module.
* **Variable Naming:** In `process_order`, `total = total + price` is better written as `total += price` for standard Pythonic brevity.

**Suggestions for Improvement**
* **Unify Loggers:** Standardize both logger classes to use a single method name (e.g., `.log()`) to remove the `hasattr` logic in `log_order`.
* **Refactor Discounts:** Move discount thresholds and rates into a configuration dictionary to flatten the `calculate_discount` logic.
* **Clean up `create_order`:** Remove `total_price` from the `create_order` arguments since it is calculated during processing.