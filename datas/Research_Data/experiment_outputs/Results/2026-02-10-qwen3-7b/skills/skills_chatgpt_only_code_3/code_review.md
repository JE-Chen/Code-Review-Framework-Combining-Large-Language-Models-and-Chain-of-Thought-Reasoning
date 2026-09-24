### Diff #1  
**Summary**  
The PR provides core functionality for order management, including order creation, discount calculation, processing, and logging. Key components include `create_order`, `calculate_discount`, `process_order`, and logging classes. The code is well-structured but contains readability issues and redundant print statements.

---

### Linting Issues  
- **Print statements**: `print("No items")` and `print("Empty order")` are used for debugging but not part of the API.  
- **Missing docstrings**: Functions lack comments explaining purpose and parameters.  
- **Unused variables**: `total` is redefined in `process_order` but not used afterward.  
- **Formatting**: `datetime.datetime.now()` is not properly formatted in `process_order`.  

**Fix Suggestions**:  
- Replace print statements with logging or return values.  
- Add docstrings for functions.  
- Remove unused variables.  

---

### Code Smells  
1. **Tight Coupling**: `process_order` relies on `datetime` and `logger` objects, making it hard to test.  
2. **Redundant Logic**: `calculate_discount` and `process_order` share similar logic for discount calculation.  
3. **Poor Naming**: `order["total_price"]` is unclear; use `order.total_price` instead.  
4. **Debugging Overload**: `process_order` prints debug info but does not return useful state.  

**Improvements**:  
- Extract shared logic into helper functions.  
- Use dependency injection for `logger` and `datetime`.  
- Rename variables for clarity.