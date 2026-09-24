- Code Smell Type: Magic Strings & Hardcoded Business Logic
- Problem Location: `calculate_discount` function (lines 21-43)
- Detailed Explanation: The discount logic is heavily reliant on hardcoded strings ("vip", "normal", "staff") and numeric thresholds. This makes the code fragile; a typo in a string will lead to silent failures (defaulting to 0 discount). Furthermore, adding a new customer type or changing a discount threshold requires modifying the core logic of the function, violating the Open/Closed Principle.
- Improvement Suggestions: Use an `Enum` for customer types and a configuration dictionary or a Strategy pattern to map customer types to their respective discount rules.
- Priority Level: High

- Code Smell Type: Inconsistent Interface (Liskov Substitution Principle Violation)
- Problem Location: `FileLogger.log`, `ConsoleLogger.write`, and `log_order` (lines 101-113)
- Detailed Explanation: `FileLogger` uses `.log()` while `ConsoleLogger` uses `.write()`. To compensate, `log_order` uses `hasattr` checks to determine which method to call. This is a "leaky abstraction" where the caller must know the internal implementation details of the logger. It makes the system difficult to extend; adding a third logger with a different method name would require changing the `log_order` logic.
- Improvement Suggestions: Define a common interface (e.g., an Abstract Base Class `Logger`) that mandates a single method name (e.g., `log()`) for all logger implementations.
- Priority Level: High

- Code Smell Type: Primitive Obsession
- Problem Location: `create_order` and `process_order` (lines 4-14, 47-87)
- Detailed Explanation: The `order` is represented as a plain dictionary, and `items` as a list of tuples. This lacks type safety and semantic clarity. Accessing data via string keys (e.g., `order["customer_type"]`) is error-prone and provides no IDE autocompletion or compile-time checks. It also mixes data storage with business logic.
- Improvement Suggestions: Replace the dictionary with a `dataclass` or a proper `Order` class. Replace the item tuples with an `OrderItem` class.
- Priority Level: Medium

- Code Smell Type: Violation of Single Responsibility Principle (SRP)
- Problem Location: `process_order` function (lines 47-87)
- Detailed Explanation: The `process_order` function is doing too many things: it validates the order, calculates the total price, applies discounts, handles logging/verbose output, and updates timestamps. This makes the function harder to test in isolation and maintain.
- Improvement Suggestions: Split the function into smaller, dedicated methods: `validate_order()`, `calculate_total()`, and `apply_discount()`. Move the `verbose` printing to a dedicated reporting or logging utility.
- Priority Level: Medium