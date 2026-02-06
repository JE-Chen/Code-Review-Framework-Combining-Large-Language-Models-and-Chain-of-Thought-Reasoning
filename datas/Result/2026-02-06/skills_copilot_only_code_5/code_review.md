### Diff #1

---

### **Summary**  
This diff introduces a global state management system with helper functions for initialization, state mutation, and data processing. The code defines a mutable global dictionary (`GLOBAL_STATE`) and five functions (`init_data`, `increment_counter`, `toggle_flag`, `process_items`, `reset_state`) that operate on this state, along with a `main` function demonstrating usage. The changes focus on centralizing state management for a simple data processing workflow, including threshold-based transformations and flag toggling.  

- **Key files affected**: Single module (e.g., `state_manager.py` or `main.py`).  
- **Plain-language explanation**: The code tracks a list of numbers (1-20), a counter, a toggle switch, and a threshold value. It processes numbers differently based on the toggle state (doubling evens, tripling odds vs. adjusting around the threshold), and resets all state to defaults.  

---

### **Linting Issues**  
No critical style/formatting violations (e.g., PEP8 compliance). Minor improvements suggested:  

| File/Line | Issue                          | Recommendation                                  |
|-----------|--------------------------------|------------------------------------------------|
| `GLOBAL_STATE` | Mutable global declared as "constant" | Use `from typing import MutableMapping` and add type hints for clarity. |
| `process_items` | Magic number `77`              | Replace with `THRESHOLD = 77` at module level. |
| `reset_state` | Unused `mode` field            | Remove `mode` from `GLOBAL_STATE` or document its purpose. |

**Rationale**:  
- The global state is named in caps (per convention), but its mutability conflicts with the "constant" implication. Type hints would improve readability.  
- Hardcoded `77` violates DRY (Don’t Repeat Yourself).  
- Unused `mode` field wastes memory and confuses readers.  

---

### **Code Smells**  
Major maintainability risks:  

1. **Global State Overuse**  
   - **Why problematic**: All functions depend on `GLOBAL_STATE`, making code hard to test, debug, or reuse. Side effects (e.g., `reset_state` changing `mode`) create hidden dependencies.  
   - **Fix**: Replace with dependency injection (e.g., pass `state` as a parameter to functions).  

2. **Dead Code**  
   - **Why problematic**: `mode` is set in `reset_state` but never used elsewhere. Unnecessary complexity.  
   - **Fix**: Remove `mode` from `GLOBAL_STATE` and `reset_state`.  

3. **Magic Threshold**  
   - **Why problematic**: The hardcoded `77` in `GLOBAL_STATE` is inflexible and error-prone.  
   - **Fix**: Define `THRESHOLD = 77` at the top.  

4. **Tight Coupling in `process_items`**  
   - **Why problematic**: The function mixes business logic (processing rules) with state access. Hard to modify without affecting other logic.  
   - **Fix**: Split into pure functions (e.g., `transform_item(item, flag, threshold)`).  

5. **Redundant Initialization**  
   - **Why problematic**: `init_data` sets `data` and `counter`, but `counter` is derived from `data`. If `data` changes, `counter` becomes stale.  
   - **Fix**: Compute `counter` on demand (e.g., `len(GLOBAL_STATE["data"])`) instead of storing it.  

**Refactoring Strategy**:  
- Eliminate global state entirely.  
- Replace `GLOBAL_STATE` with a class (e.g., `AppState`) holding all fields.  
- Make all operations pure functions that take `state` as input.  
- Example:  
  ```python
  class AppState:
      def __init__(self):
          self.data = list(range(1, 21))
          self.counter = len(self.data)
          self.flag = False
          self.threshold = 77

  def process_items(state):
      return [item * 2 if state.flag and item % 2 == 0 else ...]
  ```