# Diff #1

---

### **Summary**

This pull request introduces a basic system for creating, processing, and logging orders. It includes:

- A function to build an order (`create_order`) with fields such as customer info, items, pricing, and timestamps.
- A discount calculator (`calculate_discount`) that applies varying discounts based on customer type and purchase value.
- An order processor (`process_order`) which calculates totals, applies discounts, and records processing time.
- Printers and loggers for displaying and logging order data.

The code simulates handling a VIP customer’s order with multiple items.

For non-experts: This code models how a real-world store might manage customer orders — including applying special pricing rules and tracking what was bought.

---

### **Linting Issues**

- No clear linting errors detected in Python code style. However:
  - Missing docstrings for functions and classes.
  - Indentation is inconsistent (some lines use tabs instead of spaces).
  - Use of bare `print()` statements instead of structured logging.

**Recommendations:**
- Add docstrings to explain parameters and return values.
- Replace `print(...)` calls with proper logging utilities like `logging`.
- Ensure consistent indentation using spaces only.

---

### **Code Smells**

| Issue | Description | Why It Matters | Recommendation |
|-------|-------------|----------------|----------------|
| Magic Strings | `"vip"`, `"normal"`, `"staff"` used directly in logic | Hard to maintain or extend; unclear intent | Define constants or enums |
| Duplicated Logic | Discount calculation logic duplicated across types | Makes future updates error-prone | Extract into reusable helper |
| Tight Coupling | `log_order` checks for method existence via `hasattr` | Less predictable behavior and harder to test | Enforce interface contract or abstract base class |
| Global State Dependency | Uses `datetime.datetime.now()` without control | Makes testing difficult | Pass time as parameter or inject dependency |
| Poor Data Structure Choice | Using lists of tuples for items (`(name, price)`) | Not extensible or readable | Switch to named tuple or dict |

---