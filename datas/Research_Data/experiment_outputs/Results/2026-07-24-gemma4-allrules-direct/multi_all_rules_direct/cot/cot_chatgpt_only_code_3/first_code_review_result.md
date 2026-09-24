### Code Review

**Logic & Correctness**
* **Input Mutation:** `process_order` modifies the `order` dictionary in place. This can lead to unexpected side effects for the caller. Consider returning a new dictionary or documenting the mutation.
* **Redundant Assignment:** In `process_order`, `order["paid"] = False` is set again, despite already being initialized in `create_order`.

**Software Engineering Standards**
* **Interface Inconsistency:** `FileLogger` uses `.log()` while `ConsoleLogger` uses `.write()`. This forces `log_order` to use `hasattr` checks. Define a consistent interface (e.g., a base class or a shared method name like `log`) to ensure polymorphism.
* **Magic Numbers:** The discount rates (0.2, 0.1, 0.05, 0.3) and thresholds (1000, 500) in `calculate_discount` are hard-coded. These should be moved to named constants for better maintainability.
* **Deep Nesting:** `calculate_discount` uses nested `if/elif` blocks. This could be simplified using a lookup table (dictionary) or guard clauses to reduce cognitive load.

**Readability & Naming**
* **Variable Naming:** In `process_order`, the loop uses `item[0]` and `item[1]`. Using tuple unpacking (e.g., `for name, price in order["items"]:`) would be more descriptive and readable.

**Performance & Security**
* **Input Validation:** `process_order` checks for the existence of "items", but `calculate_discount` and `log_order` assume the `order` dictionary contains specific keys (`customer_type`, `customer_name`) without validation, which could lead to `KeyError`.