- Code Smell Type: Deeply Nested Conditional Logic
- Problem Location: `calculate_discount` function
- Detailed Explanation: The function uses nested `if-elif-else` blocks to determine discounts based on customer type and total price. This increases cognitive load and makes the logic harder to maintain or extend (e.g., adding a new customer type or changing price brackets requires modifying the core logic flow).
- Improvement Suggestions: Use a lookup table (dictionary) or a strategy pattern to map customer types to their respective discount rules. Alternatively, use guard clauses to flatten the structure.
- Priority Level: Medium

- Code Smell Type: Violation of Single Responsibility Principle (SRP)
- Problem Location: `process_order` function
- Detailed Explanation: This function is doing too many things: it validates the order, calculates the total price, applies discounts, handles logging/verbose output, and updates the order state. This makes the function harder to test in isolation and reuse.
- Improvement Suggestions: Split the function into smaller, focused functions: `validate_order()`, `calculate_total()`, and `apply_discount()`. Move the `verbose` printing to a dedicated logging or reporting utility.
- Priority Level: Medium

- Code Smell Type: Inconsistent Interface / Tight Coupling
- Problem Location: `log_order` function and `FileLogger`/`ConsoleLogger` classes
- Detailed Explanation: The `log_order` function relies on `hasattr` to check for either `.log()` or `.write()` methods. This indicates a lack of a common interface (contract) between logger implementations. It forces the caller to know the internal method names of various logger classes, which is fragile and violates polymorphism.
- Improvement Suggestions: Define a base class or an Abstract Base Class (ABC) `Logger` with a standard method (e.g., `log()`). Ensure all logger implementations inherit from this base class and implement the same method.
- Priority Level: High

- Code Smell Type: Magic Numbers
- Problem Location: `calculate_discount` function (e.g., `1000`, `500`, `0.2`, `0.1`, `0.05`)
- Detailed Explanation: Hard-coded numeric values for price thresholds and discount rates are scattered throughout the logic. If these business rules change, developers must hunt through the code to update every instance, increasing the risk of inconsistency.
- Improvement Suggestions: Move these values into named constants at the top of the module or a configuration file (e.g., `VIP_HIGH_THRESHOLD = 1000`, `VIP_HIGH_DISCOUNT = 0.2`).
- Priority Level: Low

- Code Smell Type: Modifying Input Arguments
- Problem Location: `process_order` function
- Detailed Explanation: The function modifies the `order` dictionary in place (e.g., `order["total_price"] = total`, `order["final_price"] = final_price`). This can lead to surprising side effects for the caller, as the original object is mutated.
- Improvement Suggestions: Create a copy of the order dictionary inside the function or return a new "ProcessedOrder" object/dataclass to maintain immutability of the input.
- Priority Level: Medium