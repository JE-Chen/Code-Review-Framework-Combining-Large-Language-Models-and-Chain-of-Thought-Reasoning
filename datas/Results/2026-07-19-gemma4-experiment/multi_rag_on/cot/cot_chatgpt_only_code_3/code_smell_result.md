- Code Smell Type: Primitive Obsession / Lack of Domain Modeling
- Problem Location: `create_order` function and throughout the codebase (e.g., `order = {}`)
- Detailed Explanation: The system uses a plain dictionary to represent an `Order` and tuples for `Items`. This lacks type safety and makes the code fragile. For example, `process_order` must manually check if `"items" in order` because there is no guaranteed schema. Accessing data via string keys (e.g., `order["customer_type"]`) is prone to typos and makes refactoring difficult as the project grows.
- Improvement Suggestions: Replace the dictionary with a `dataclass` or a `NamedTuple`. Create a specific `Item` class instead of using tuples.
- Priority Level: High

- Code Smell Type: Violation of Open/Closed Principle (Conditional Complexity)
- Problem Location: `calculate_discount` function
- Detailed Explanation: The function uses a nested `if-elif-else` structure to determine discounts based on `customer_type`. Every time a new customer type is added or a discount tier changes, this function must be modified. This increases the risk of introducing bugs into existing logic when adding new features.
- Improvement Suggestions: Use a Strategy pattern or a lookup table (dictionary) that maps customer types to their respective discount logic or rate tiers.
- Priority Level: Medium

- Code Smell Type: Interface Inconsistency / Lack of Polymorphism
- Problem Location: `log_order` function and `FileLogger`/`ConsoleLogger` classes
- Detailed Explanation: `FileLogger` uses a method named `log()`, while `ConsoleLogger` uses `write()`. To handle this, `log_order` uses `hasattr()` checks to determine which method to call. This is a "leaky abstraction" and defeats the purpose of using classes for logging; the caller should not need to know the internal method names of the logger.
- Improvement Suggestions: Define a common interface (e.g., an Abstract Base Class `Logger`) that enforces a single method name (e.g., `log()`) for all logger implementations.
- Priority Level: Medium

- Code Smell Type: Unclear Naming / Magic Indices
- Problem Location: `process_order` loop: `name = item[0]`, `price = item[1]`
- Detailed Explanation: Using integer indices (`[0]`, `[1]`) to access data is opaque. A developer reading the code must remember that index 0 is the name and index 1 is the price. This reduces readability and increases the likelihood of errors if the tuple structure changes.
- Improvement Suggestions: Use named tuples or a class for items, or use unpacking: `for name, price in order["items"]:`.
- Priority Level: Low