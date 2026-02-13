### PR Summary

- **Key Changes**: State management, processing logic, and reset functionality enhanced.  
- **Impact Scope**: Main function, `process_items()`, and `reset_state()`.  
- **Purpose**: Handle dynamic thresholds, toggle flags, and reset states.  
- **Risks**: Edge cases (e.g., threshold invalid, flag misuse) require testing.  
- **Confirm Items**: State consistency, logic correctness, and test coverage.  

---

### Code Review

#### 1. **Readability & Consistency**  
- ✅ Indentation and formatting are consistent.  
- ❌ Global state (`GLOBAL_STATE`) lacks clarity. Refactor to class-based state management.  
- ❌ Function names are terse (e.g., `toggle_flag()`). Add docstrings.  

---

#### 2. **Naming Conventions**  
- ✅ Functions like `toggle_flag()` are descriptive.  
- ❌ Global state names (e.g., `GLOBAL_STATE`) are inconsistent. Use `state` or `config`.  

---

#### 3. **Software Engineering Standards**  
- ✅ Modular logic (e.g., `init_data()`, `process_items()`).  
- ❌ Duplicate code (e.g., flag toggling in `toggle_flag()` and `process_items()`).  
- ✅ Reset state is called but not used elsewhere. Refactor for clarity.  

---

#### 4. **Logic & Correctness**  
- ✅ `process_items()` handles flag and threshold logic.  
- ❌ Threshold validation missing (e.g., if `threshold` is invalid).  
- ❌ Edge cases (e.g., empty `data` list) not handled.  

---

#### 5. **Performance & Security**  
- ✅ No performance bottlenecks.  
- ❌ Input validation missing (e.g., threshold values).  

---

#### 6. **Documentation & Testing**  
- ✅ `main()` includes print statements.  
- ❌ No tests or docstrings for functions.  

---

### Recommendations  
- Replace `GLOBAL_STATE` with a class.  
- Add docstrings to functions.  
- Refactor `reset_state()` and `process_items()` for clarity.  
- Add unit tests for edge cases.