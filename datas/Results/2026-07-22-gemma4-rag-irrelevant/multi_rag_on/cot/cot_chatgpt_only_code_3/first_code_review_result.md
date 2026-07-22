### Code Review

**Logic & Correctness**
* **Redundant Parameter:** In `create_order`, `total_price` is passed as an argument but is immediately overwritten by the calculation in `process_order`. This creates confusion about the source of truth for the order total.
* **Inconsistent Logger Interface:** `FileLogger` uses `.log()` while `ConsoleLogger` uses `.write()`. This forces `log_order` to use `hasattr` checks, violating the principle of polymorphism.

**Software Engineering Standards**
* **Data Structure:** Using dictionaries for `order` makes the code fragile (prone to `KeyError`). Consider using a `dataclass` or `NamedTuple` for better type safety and readability.
* **Modularity:** The `calculate_discount` function contains hardcoded business rules. Moving these to a configuration mapping or a strategy pattern would make the system easier to maintain.
* **Class Design:** `OrderPrinter` does not maintain any state; its `print_order` method should likely be a static method or a standalone function.

**Readability & Consistency**
* **Naming:** Variable names are generally descriptive and clear.
* **Formatting:** Indentation and spacing follow standard Python conventions.

**Suggestions for Improvement**
* **Unify Logger Interface:** Define a base class or a consistent method name (e.g., `.log()`) for all logger classes to remove the `if/elif` chain in `log_order`.
* **Refactor Discount Logic:** Use a dictionary to map `customer_type` to discount thresholds to reduce the nested `if/elif` blocks.
* **Remove Unused Parameter:** Remove `total_price` from `create_order` since it is calculated during processing.