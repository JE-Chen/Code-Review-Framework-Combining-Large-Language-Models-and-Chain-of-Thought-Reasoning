### 📝 Pull Request Summary

- **Key Changes**  
  - Introduced modular exporters (`TextExporter`, `UpperTextExporter`, `JsonLikeExporter`) based on configuration.
  - Added `ReportFormatter` to process report content.
  - Implemented `ExportManager` and `ReportService` for orchestrating export workflows.

- **Impact Scope**  
  - Affects core reporting logic and export behavior via configurable formats.
  - Extends support for different output types (text, JSON-like) without modifying base classes.

- **Purpose of Changes**  
  - Enables flexible reporting with dynamic export strategies using dependency injection and configuration-driven selection.

- **Risks and Considerations**  
  - Potential misuse of global `CONFIG` dict may affect test isolation or concurrency.
  - `BaseExporter.finish()` is overriden inconsistently; some implementations do nothing.

- **Items to Confirm**  
  - Ensure thread safety of `CONFIG` during concurrent runs.
  - Validate that all exporters properly implement required methods.
  - Test edge cases like empty rows or invalid configurations.

---

### ✅ Code Review Findings

#### 1. **Readability & Consistency**
- ✅ Good use of class hierarchy and method separation.
- ⚠️ Inconsistent indentation in multiline strings.
- ⚠️ Use of raw string concatenation (`+`) instead of f-strings or `.join()` where appropriate.

#### 2. **Naming Conventions**
- ✅ Clear naming (`TextExporter`, `ReportService`, etc.) reflects purpose.
- ⚠️ `after_export()` lacks a descriptive name; consider renaming for clarity.

#### 3. **Software Engineering Standards**
- ✅ Modular design supports extensibility.
- ⚠️ Duplicated logic in `ReportFormatter` can be simplified.
- ⚠️ Global variable `CONFIG` introduces tight coupling and makes testing harder.

#### 4. **Logic & Correctness**
- ✅ No obvious logic errors found.
- ⚠️ `finish()` method is unused or inconsistently implemented — consider removing or enforcing usage.
- ⚠️ `buffer += ch` loop could be replaced with direct string usage for better readability.

#### 5. **Performance & Security**
- ⚠️ No major performance issues detected.
- ⚠️ Hardcoded string concatenation in `JsonLikeExporter` may lead to maintainability issues.

#### 6. **Documentation & Testing**
- ⚠️ Missing docstrings for key functions and classes.
- ⚠️ No unit tests provided — critical for verifying behavior under various configurations.

#### 7. **Additional Suggestions**
- Replace global `CONFIG` with an injected config object.
- Move hardcoded strings into constants or config values.
- Add optional logging or metrics tracking in `ExportManager`.

---

### 💡 Overall Assessment

This code demonstrates good structural patterns but has room for improvement in modularity, testability, and robustness. Addressing global state and duplication will improve long-term maintainability.