### Code Review

**Logic & Correctness**
* **Redundant Parameter:** In `create_order`, `total_price` is passed as an argument but is immediately overwritten by the sum calculation in `process_order`. This creates a misleading API.
* **Inconsistent Logger Interface:** `log_order` uses `hasattr` to check for `.log()` or `.write()`. This violates the Dependency Inversion Principle. Loggers should implement a common interface/abstract base class.

**Software Engineering Standards**
* **Data Structure:** Using dictionaries for `order` makes the code fragile (prone to `KeyError`). Using a `dataclass` or `NamedTuple` would provide better type safety and readability.
* **Modularity:** `calculate_discount` contains hardcoded business rules. These should be moved to a configuration object or a mapping to make the logic easier to maintain without modifying the function.
* **Class Design:** `OrderPrinter` does not maintain any state; the `print_order` method should be a static method or a standalone function.

**Readability & Naming**
* **Naming:** Variable names are generally descriptive and clear.
* **Formatting:** Indentation and spacing follow PEP 8 standards.

**Suggestions for Improvement**
* **Refactor Loggers:** Define a base `Logger` class with a `log()` method that both `FileLogger` and `ConsoleLogger` inherit from.
* **Simplify `calculate_discount`:** Use a dictionary to map `customer_type` to discount thresholds to eliminate the deeply nested `if/elif` blocks.
* **Remove `total_price` from `create_order`:** Since the total is calculated during processing, remove it from the creation step to avoid confusion.