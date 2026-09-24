- Code Smell Type: Primitive Obsession / Lack of Domain Modeling
- Problem Location: `create_order` function and throughout the codebase (e.g., `order["customer_type"]`, `order["items"]`).
- Detailed Explanation: The code uses basic dictionaries and tuples to represent complex domain entities (Orders, Customers, Items). This leads to "stringly-typed" logic (e.g., checking `if customer_type == "vip"`), which is error-prone. If a key name changes or a typo occurs in a string literal, the program will fail at runtime rather than being caught by a type checker or IDE. It also makes the code harder to maintain as the "schema" of the order is implicit rather than explicit.
- Improvement Suggestions: Replace the dictionary with a `dataclass` or a `class`. Use an `Enum` for `customer_type` to ensure type safety and avoid magic strings.
- Priority Level: High

- Code Smell Type: Violation of Open/Closed Principle (OCP)
- Problem Location: `calculate_discount` function.
- Detailed Explanation: The function uses a series of `if/elif` blocks to determine discounts based on customer types. Every time a new customer type is added (e.g., "Gold", "Platinum"), this function must be modified. This makes the logic fragile and increases the risk of introducing bugs into existing discount calculations when adding new ones.
- Improvement Suggestions: Implement a Strategy Pattern. Create a mapping or a set of discount strategy classes/functions where each customer type is associated with its own discount logic.
- Priority Level: Medium

- Code Smell Type: Interface Inconsistency / Tight Coupling
- Problem Location: `log_order` function and `FileLogger`/`ConsoleLogger` classes.
- Detailed Explanation: The `log_order` function uses `hasattr` to check whether to call `.log()` or `.write()`. This indicates that the logger classes do not share a common interface. The calling code is forced to "guess" the method name, which defeats the purpose of polymorphism and makes the system difficult to extend with new logger types.
- Improvement Suggestions: Define a base `Logger` abstract base class (ABC) with a standardized method (e.g., `log()`). Ensure all logger implementations override this method.
- Priority Level: Medium

- Code Smell Type: Magic Numbers
- Problem Location: `calculate_discount` function (e.g., `0.2`, `0.1`, `1000`, `500`).
- Detailed Explanation: The discount rates and price thresholds are hardcoded directly into the logic. This makes it difficult to update business rules (e.g., changing the VIP threshold from 1000 to 1200) without hunting through the implementation details of the function.
- Improvement Suggestions: Move these values to named constants at the top of the module or into a configuration file (e.g., `VIP_HIGH_THRESHOLD = 1000`).
- Priority Level: Low