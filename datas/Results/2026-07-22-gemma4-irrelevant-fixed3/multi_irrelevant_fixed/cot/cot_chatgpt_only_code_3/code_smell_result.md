- Code Smell Type: Magic Strings & Hardcoded Business Logic
- Problem Location: `calculate_discount` function
- Detailed Explanation: The discount logic relies on hardcoded strings ("vip", "normal", "staff") and numeric thresholds (1000, 500). This makes the code fragile; a typo in a string will lead to silent failures (defaulting to 0 discount). Furthermore, changing a business rule requires modifying the core logic of the function, violating the Open/Closed Principle.
- Improvement Suggestions: Use an `Enum` for customer types and move the discount thresholds into a configuration object or a mapping dictionary.
- Priority Level: High

- Code Smell Type: Primitive Obsession / Lack of Type Safety
- Problem Location: `create_order` and `process_order` (use of dictionaries and tuples)
- Detailed Explanation: The system uses generic dictionaries for `order` and tuples for `items`. This lacks semantic clarity and makes the code prone to `KeyError` or `IndexError` (e.g., `item[0]`, `item[1]`). It forces the developer to remember the exact structure of the dictionary across different functions, increasing the risk of bugs during maintenance.
- Improvement Suggestions: Replace the dictionary with a `dataclass` or a named class (e.g., `Order` and `OrderItem`). This provides autocomplete support, type hinting, and a formal schema.
- Priority Level: High

- Code Smell Type: Violation of Interface Segregation / Liskov Substitution (Inconsistent API)
- Problem Location: `log_order` function and `FileLogger`/`ConsoleLogger` classes
- Detailed Explanation: The `log_order` function uses `hasattr` to check for either `.log()` or `.write()`. This indicates that the logger classes do not share a common interface. This "duck typing" approach is brittle and forces the calling function to implement conditional logic to handle different logger implementations.
- Improvement Suggestions: Define a base `Logger` abstract base class (ABC) with a single method (e.g., `log()`). Ensure all logger implementations inherit from this base class.
- Priority Level: Medium

- Code Smell Type: Mixed Responsibilities (Violation of SRP)
- Problem Location: `process_order` function
- Detailed Explanation: The `process_order` function is doing too many things: it validates the order, calculates the total price, applies discounts, and handles logging/verbose output. This makes the function harder to test in isolation and harder to reuse.
- Improvement Suggestions: Split the function into smaller, focused utilities: `validate_order()`, `calculate_total()`, and `apply_discount()`.
- Priority Level: Medium