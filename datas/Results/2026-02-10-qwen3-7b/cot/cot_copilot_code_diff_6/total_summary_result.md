### PR Total Summary
- **Overall Conclusion**: Reject merge with critical code smells and missing logging.  
- **Blocking Concerns**: Logic complexity, global state, and lack of tests.  

---

### Comprehensive Evaluation
1. **Code Quality & Correctness**  
   - **Issues**: Long function with multiple responsibilities, global state, and missing error logging.  
   - **Fix Needs**: Modular separation, scoped state, and explicit exception handling.  

2. **Maintainability & Design**  
   - **Code Smells**: Poor naming (`GLOBAL_SESSION`), redundant logic, and hardcoded URLs.  
   - **Impact**: Hard to test, debug, or refactor.  

3. **Consistency**  
   - **Standards**: Violates team conventions (e.g., snake_case variables, docstrings).  

---

### Final Decision Recommendation  
**Reject merge**  
- **Reason**: Core issues (logging, naming, and separation of concerns) block clean code adoption.  

---

### Team Follow-Up  
- **Action**: Refactor into smaller functions, centralize logging, and add tests.  
- **Priority**: High.