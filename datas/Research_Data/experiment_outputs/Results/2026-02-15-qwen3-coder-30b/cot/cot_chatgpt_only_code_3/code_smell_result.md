### Code Smell Type: Magic Strings
- **Problem Location:** `create_order` and `calculate_discount`
- **Detailed Explanation:** The string values `"vip"`, `"normal"`, and `"staff"` appear directly in the code without any abstraction or constants. This makes it hard to change these values later and introduces errors if typos occur.
- **Improvement Suggestions:** Define constants or an enum for customer types to ensure consistency and prevent typo-related bugs.
- **Priority Level:** High

---

### Code Smell Type: Lack of Input Validation
- **Problem Location:** `process_order`
- **Detailed Explanation:** There's no validation of input parameters such as whether `order["items"]` is correctly formatted or `order["total_price"]` is valid. This can lead to runtime exceptions or incorrect behavior.
- **Improvement Suggestions:** Add checks to validate inputs before processing them, especially around expected data structures like item tuples.
- **Priority Level:** Medium

---

### Code Smell Type: Duplicated Logic in Discount Calculation
- **Problem Location:** `calculate_discount`
- **Detailed Explanation:** Similar logic exists within different branches (`if customer_type == "vip"` and `elif customer_type == "normal"`), which violates DRY principles. It’s also harder to extend when new customer types are added.
- **Improvement Suggestions:** Refactor discount calculation into a lookup table or dictionary mapping customer type to discount rules.
- **Priority Level:** Medium

---

### Code Smell Type: Poor Abstraction and Coupling
- **Problem Location:** `log_order`
- **Detailed Explanation:** The logging function uses duck typing (`hasattr`) instead of explicit interfaces, making dependencies unclear and fragile. Also, mixing concerns between logging and order handling.
- **Improvement Suggestions:** Use proper interface definitions or abstract base classes for loggers to enforce contracts and reduce coupling.
- **Priority Level:** Medium

---

### Code Smell Type: Inconsistent Data Structure Usage
- **Problem Location:** `create_order`, `process_order`
- **Detailed Explanation:** Using dictionaries with string keys makes the code brittle and less maintainable compared to using dedicated classes or named tuples. This hinders IDE support and static analysis.
- **Improvement Suggestions:** Replace dictionary-based orders with a class or dataclass to provide structure, type hints, and better encapsulation.
- **Priority Level:** High

---

### Code Smell Type: Hardcoded Values
- **Problem Location:** `calculate_discount`
- **Detailed Explanation:** Thresholds like `1000`, `500` are hardcoded and not configurable. This reduces flexibility and makes changes more error-prone.
- **Improvement Suggestions:** Extract thresholds into configuration variables or a separate module that defines pricing tiers.
- **Priority Level:** Medium

---

### Code Smell Type: Side Effects in Core Functions
- **Problem Location:** `process_order`, `print_order`
- **Detailed Explanation:** Functions like `process_order` have side effects (modifies `order`, prints to console) that make testing difficult and reduce predictability.
- **Improvement Suggestions:** Separate pure logic from side-effectful operations. For instance, let printing and modification happen in distinct steps or via callbacks.
- **Priority Level:** High

---

### Code Smell Type: Unused Fields
- **Problem Location:** `create_order`
- **Detailed Explanation:** The `total_price` field is passed but then recalculated inside `process_order`. This creates redundancy and confusion about where the value comes from.
- **Improvement Suggestions:** Either compute and set `total_price` at creation time or remove it from initial setup.
- **Priority Level:** Medium

---

### Code Smell Type: Missing Type Hints
- **Problem Location:** All functions
- **Detailed Explanation:** No type annotations are used, reducing readability and maintainability. It also prevents tools like mypy from catching potential issues early.
- **Improvement Suggestions:** Add appropriate type hints for parameters and return types.
- **Priority Level:** Low

---

### Code Smell Type: Poor Error Handling
- **Problem Location:** `process_order`
- **Detailed Explanation:** Errors are printed rather than raised or handled gracefully. This makes debugging harder and doesn’t allow callers to react appropriately.
- **Improvement Suggestions:** Raise exceptions on invalid states or return error codes/objects instead of just printing messages.
- **Priority Level:** Medium

---

### Code Smell Type: Misuse of Global State
- **Problem Location:** `process_order`
- **Detailed Explanation:** Default parameter `now=None` with fallback to `datetime.datetime.now()` can be problematic in concurrent environments or during testing due to implicit reliance on system clock.
- **Improvement Suggestions:** Pass time explicitly or use dependency injection for time sources to enable deterministic behavior in tests.
- **Priority Level:** Medium

---