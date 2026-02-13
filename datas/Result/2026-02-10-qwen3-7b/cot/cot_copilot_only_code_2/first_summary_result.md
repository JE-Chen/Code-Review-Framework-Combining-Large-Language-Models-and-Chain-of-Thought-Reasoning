### PR Summary

- **Key Changes**: Added `StringProcessor`, `NumberProcessor`, and `DataPipeline` classes; updated `main()` to use pipeline.  
- **Impact Scope**: Affected `DataPipeline`, `StringProcessor`, `NumberProcessor`, and `main()`.  
- **Purpose**: Unified data processing pipeline and validated core logic.  
- **Risks**: Missing error handling for invalid data types or config.  
- **Confirm Items**: Processor correctness, pipeline logic, config usage, and edge case coverage.  

---

### Code Review Details

#### 1. **Readability & Consistency**
- **Indentation**: Consistent with Python standards (4 spaces).  
- **Formatting**: Clean spacing between method definitions.  
- **Comments**: Minimal; add docstrings to clarify logic.  

---

#### 2. **Naming Conventions**
- **Class Names**: Clear and consistent (`BaseProcessor`, `StringProcessor`, `NumberProcessor`).  
- **Method Names**: Descriptive (`process()`, `run()`).  

---

#### 3. **Software Engineering Standards**
- **Modularity**: Each processor handles a distinct task.  
- **Testability**: `main()` includes basic validation but lacks unit tests.  
- **Abstraction**: `DataPipeline` manages processor sequence.  

---

#### 4. **Logic & Correctness**
- **Processor Logic**:  
  - `StringProcessor` converts letters to uppercase and non-letters to ASCII.  
  - `NumberProcessor` applies mathematical transformation.  
- **Edge Cases**:  
  - No validation for invalid input types (e.g., `None` or non-string numbers).  
  - No handling of empty input.  

---

#### 5. **Performance & Security**
- **Performance**: O(n) time complexity for processors.  
- **Security**: `GLOBAL_CONFIG` used without validation; expose config for external modification.  

---

#### 6. **Documentation & Testing**
- **Documentation**: Minimal comments in `main()` and classes.  
- **Testing**: No unit tests; `main()` includes basic assertions.  

---

### ✅ Recommendations
- Add docstrings to `process()` and `run()` methods.  
- Validate `GLOBAL_CONFIG` values in `main()`.  
- Expand unit tests for edge cases (e.g., empty input, invalid types).