### Pull Request Summary

*   **Key changes**: Implemented a basic order processing system including order creation, discount calculation based on customer type, and a logging/printing mechanism.
*   **Impact scope**: New order management logic and utility classes for logging and printing.
*   **Purpose of changes**: Establish a foundation for handling customer orders and applying business rules for pricing.
*   **Items to confirm**: Review the discount logic for correctness and the flexibility of the logger implementation.

---

### Code Review

#### 1. Readability & Consistency
*   **Formatting**: The code is generally clean and follows standard Python indentation.
*   **Consistency**: The use of `print` statements for both business logic errors (e.g., "No items") and debugging (`verbose=True`) is inconsistent. Consider using a proper logging framework.

#### 2. Naming Conventions
*   **Descriptive Names**: Variable and function names are clear and semantic (e.g., `calculate_discount`, `process_order`).

#### 3. Software Engineering Standards
*   **Modularization**: The logic is split into functions, but the `log_order` function violates the **Interface Segregation Principle** and **Liskov Substitution Principle**. It uses `hasattr` to check for `log` vs `write`, which is a "code smell."
    *   *Recommendation*: Define a common `Logger` base class or protocol that enforces a single method name (e.g., `log()`) for all logger implementations.
*   **Data Structures**: Using dictionaries for `order` objects makes the code prone to `KeyError` and lacks type safety.
    *   *Recommendation*: Use a `dataclass` or a `NamedTuple` for the Order entity.

#### 4. Logic & Correctness
*   **Redundant Assignment**: In `create_order`, `total_price` is passed as an argument, but in `process_order`, it is completely recalculated and overwritten (`order["total_price"] = total`). This makes the initial argument in `create_order` misleading or useless.
*   **Boundary Conditions**:
    *   The `calculate_discount` function handles unknown `customer_type` values gracefully by returning `0`.
    *   `process_order` handles empty item lists, though it returns the order object without processing, which might lead to missing keys (like `final_price`) in the calling function.

#### 5. Performance & Security
*   **Performance**: The time and space complexity are optimal for the current scope ($O(N)$ where $N$ is the number of items).
*   **Security**: No external inputs are handled, so there are no immediate injection risks. However, the use of `print` for error handling is not suitable for production environments.

#### 6. Documentation & Testing
*   **Documentation**: The code lacks docstrings. While the logic is simple, the business rules for discounts should be documented.
*   **Testing**: No unit tests are provided. The `main()` function serves as a manual smoke test, but automated tests are needed to verify the discount tiers.

### Summary of Recommendations
| Priority | Category | Issue | Suggestion |
| :--- | :--- | :--- | :--- |
| **High** | Engineering | Logger interface inconsistency | Use a base class/interface for `FileLogger` and `ConsoleLogger`. |
| **Medium** | Logic | Redundant `total_price` | Remove `total_price` from `create_order` if it's always recalculated. |
| **Medium** | Engineering | Dictionary-based entities | Replace `order` dictionary with a `dataclass`. |
| **Low** | Testing | Lack of automation | Implement unit tests for `calculate_discount`. |