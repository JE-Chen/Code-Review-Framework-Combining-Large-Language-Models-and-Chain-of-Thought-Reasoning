### Code Review Summary

#### 1. **Readability & Consistency**
- ✅ Indentation and structure are consistent.
- ⚠️ Comments are missing; adding brief inline comments would improve clarity.

#### 2. **Naming Conventions**
- ❌ Global state variables like `GLOBAL_STATE` and `counter`, `data`, etc., lack context and are not descriptive.
- ⚠️ Function names (`init_data`, `process_items`) are okay but could benefit from more explicit descriptions if used in larger systems.

#### 3. **Software Engineering Standards**
- ❌ Heavy reliance on global mutable state reduces modularity and testability.
- ⚠️ Logic is duplicated in conditional branches inside `process_items()`—could be refactored into helper functions.

#### 4. **Logic & Correctness**
- ✅ No major logic flaws detected.
- ⚠️ The flag toggling and threshold-based processing may behave unexpectedly without clear intent or validation.

#### 5. **Performance & Security**
- ⚠️ Global state usage can lead to race conditions or side effects in concurrent environments.
- ✅ No direct security issues identified; however, input assumptions aren't validated.

#### 6. **Documentation & Testing**
- ❌ Missing docstrings or inline documentation for functions.
- ⚠️ No unit tests provided—hard to verify behavior under edge cases.

#### 7. **Suggestions**
- Replace global mutable state with parameters and return values where possible.
- Add descriptive comments and docstrings.
- Refactor repeated logic into reusable helpers.
- Consider testing each function independently.

--- 

### Specific Feedback Points

- **Global State Usage**: Avoid using `GLOBAL_STATE` directly. Pass state as arguments for better encapsulation.
- **Function Naming**: Improve clarity: e.g., `process_items()` → `transform_items_based_on_mode()`.
- **Code Duplication**: Move conditionals in `process_items()` into separate functions for reuse.
- **Missing Docs**: Add basic docstrings explaining what each function does.
- **Testing**: Include simple unit tests for `process_items()` with known inputs/outputs.

--- 

### Score: ⚠️ Needs Improvement  
**Reason:** Overuse of global variables and lack of modularity make code fragile and hard to extend. Addressing these will greatly improve maintainability.