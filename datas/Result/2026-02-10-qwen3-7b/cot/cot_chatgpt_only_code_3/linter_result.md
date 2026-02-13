### Linter Messages

1. **rule_id**: `no-empty-blocks`  
   **severity**: **error**  
   **message**: Block `if now is None` is empty.  
   **line**: 11  
   **suggestion**: Add a comment or explicit `if`/`else` block.  

2. **rule_id**: `no-duplicate-code`  
   **severity**: **warning**  
   **message**: Code duplication in `create_order` and `process_order`.  
   **line**: 14  
   **suggestion**: Extract common logic into helper functions.  

3. **rule_id**: `no-unused-vars`  
   **severity**: **warning**  
   **message**: Variable `order` is unused in `process_order`.  
   **line**: 16  
   **suggestion**: Remove or rename unused variable.  

4. **rule_id**: `no-implicit-boolean`  
   **severity**: **error**  
   **message**: Boolean expression `total > 1000` is not explicitly evaluated.  
   **line**: 24  
   **suggestion**: Add explicit `if`/`else` for clarity.  

5. **rule_id**: `no-implicit-boolean`  
   **severity**: **error**  
   **message**: Boolean expression `total > 500` is not explicitly evaluated.  
   **line**: 25  
   **suggestion**: Add explicit `if`/`else` for clarity.  

6. **rule_id**: `no-implicit-boolean`  
   **severity**: **error**  
   **message**: Boolean expression `discount = 0.3` is not explicitly evaluated.  
   **line**: 33  
   **suggestion**: Add explicit `if`/`else` for clarity.  

7. **rule_id**: `no-implicit-boolean`  
   **severity**: **error**  
   **message**: Boolean expression `discount = 0` is not explicitly evaluated.  
   **line**: 34  
   **suggestion**: Add explicit `if`/`else` for clarity.  

8. **rule_id**: `no-implicit-boolean`  
   **severity**: **error**  
   **message**: Boolean expression `discount = 0.05` is not explicitly evaluated.  
   **line**: 35  
   **suggestion**: Add explicit `if`/`else` for clarity.  

9. **rule_id**: `no-implicit-boolean`  
   **severity**: **error**  
   **message**: Boolean expression `discount = 0.2` is not explicitly evaluated.  
   **line**: 36  
   **suggestion**: Add explicit `if`/`else` for clarity.  

---

### Summary of Issues
- **Readability**: Inconsistent indentation and missing docstrings.  
- **Code Duplication**: Repeated logic in `create_order` and `process_order`.  
- **Missing Explicit Logic**: Boolean expressions lack explicit `if`/`else`.  
- **Unused Variables**: Redundant variables like `order`.