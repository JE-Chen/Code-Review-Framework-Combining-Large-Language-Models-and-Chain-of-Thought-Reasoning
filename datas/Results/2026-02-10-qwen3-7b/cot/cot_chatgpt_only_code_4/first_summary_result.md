### 📋 PR Summary Template

- **Summary**:  
  - **Key Changes**: Added `ReportFormatter` and `ReportService` to manage report formatting and export logic.  
  - **Impact Scope**: Affected `BaseExporter`, `ReportFormatter`, `ReportService`, and `ExportManager`.  
  - **Purpose**: Unified report formatting and export process.  
  - **Risks**: Potential issues with format handling and export manager logic.  
  - **Confirm Items**: Docstrings, test cases, and format handling correctness.  

---

### ✅ Code Review Details

#### 1. **Readability & Consistency**  
- **Indentation**: Consistent 4-space indentation.  
- **Comments**: Missing inline comments for logic clarity.  
- **Docstrings**: Missing for classes and methods.  

---

#### 2. **Naming Conventions**  
- **Class Names**: Semantic clarity (e.g., `BaseExporter`).  
- **Method Names**: Descriptive (e.g., `format()`, `generate()`).  
- **Proposals**:  
  - `ReportFormatter` → `ReportFormatter` (no change).  
  - `ExportManager` → `ExportHandler` (simpler name).  

---

#### 3. **Software Engineering Standards**  
- **Duplication**: `prepare()` method repeated across exporters.  
- **Refactor**: Extract `prepare()` into a helper function.  
- **Modularity**: `ReportService` encapsulates export logic.  

---

#### 4. **Logic & Correctness**  
- **Bug**: `ReportFormatter.format()` assumes `rows` are strings.  
- **Fix**: Validate input types.  
- **Boundary Conditions**: No handling of empty `rows`.  

---

#### 5. **Performance & Security**  
- **No Bottlenecks**: Minimal I/O operations.  
- **Security**: No input validation in `CONFIG`.  

---

#### 6. **Documentation & Testing**  
- **Docstrings**: Missing for classes and methods.  
- **Tests**: No unit tests provided.  

---

### 📌 Suggestions for Improvement  
1. Add docstrings to classes and methods.  
2. Extract `prepare()` into a helper function.  
3. Add input validation in `ReportFormatter`.  
4. Add unit tests for export logic.  

---

### ✅ Final Score: ⭐⭐⭐⭐⭐ (4/5)