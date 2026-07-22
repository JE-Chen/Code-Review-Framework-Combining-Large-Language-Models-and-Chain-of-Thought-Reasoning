### Code Review Feedback

---

**1. Readability & Consistency**  
- **Issue**: Global variables (`GLOBAL_DATA_THING`, `GLOBAL_FLAG`) are not encapsulated and used as global state.  
- **Fix**: Encapsulate these in class attributes or pass them explicitly.  

---

**2. Naming Conventions**  
- **Issue**: Function names (`make_data_somehow`, `analyze_in_a_hurry`) are vague and lack semantic clarity.  
- **Fix**: Use descriptive names like `generate_data`, `process_analysis`.  

---

**3. Software Engineering Standards**  
- **Issue**: Shared mutable state (`GLOBAL_FLAG`, `GLOBAL_DATA_THING`) introduces coupling and test complexity.  
- **Fix**: Encapsulate state in class attributes or pass it explicitly.  

---

**4. Logic & Correctness**  
- **Issue**: `do_something_questionable` lacks clear logic and boundary checks.  
- **Fix**: Add comments and validate conditions (e.g., `random.random() > 0.7`).  

---

**5. Performance & Security**  
- **Issue**: `time.sleep()` is used in UI loops, which may impact responsiveness.  
- **Fix**: Replace with async or non-blocking calls if possible.  

---

**6. Documentation & Testing**  
- **Issue**: Missing docstrings and test stubs for core functions.  
- **Fix**: Add docstrings and write unit tests for critical paths.  

---

**7. RAG Rules**  
- **Issue**: Global state is not encapsulated, violating RAG principles.  
- **Fix**: Use class attributes or pass state explicitly.  

---

### Summary of Fixes  
- **Encapsulate global state** in class attributes.  
- **Improve function and variable names** for clarity.  
- **Add comments and test stubs** for critical logic.  
- **Refactor UI logic** to reduce side effects.