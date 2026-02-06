### Report Exporter System with Configurable Output Formats

**Overview**  
A flexible report generation system that formats and exports reports in text or JSON-like formats, configurable via global settings. Uses strategy pattern for exporters and processes reports through a pipeline of formatting and exporting steps.

---

### Detailed Explanation

#### Core Components & Flow
1. **Configuration (Global `CONFIG`)**  
   - Defines default behavior:  
     ```python
     CONFIG = {
         "export_format": "text",  # Output format
         "uppercase": False,       # Convert text to uppercase
         "retry": 3                # Unused in current code
     }
     ```
   - *Assumption*: Configuration is static and global (not recommended for production).

2. **Exporter Strategy (Base Class)**  
   - `BaseExporter` enforces `prepare()`, `export()`, and `finish()` interfaces.  
   - *Edge Case*: `finish()` is unused in the main flow (commented as "preparatory").

3. **Concrete Exporters**  
   - **TextExporter**:  
     - `prepare()`: Returns data unchanged.  
     - `export()`: Prints data with "TEXT EXPORT:" header.  
   - **UpperTextExporter**:  
     - `prepare()`: Converts data to uppercase.  
     - *Example Output*: `UPPER TEXT EXPORT:\nAPPLE 10`  
   - **JsonLikeExporter**:  
     - `prepare()`: Wraps data in a *non-valid* JSON string (e.g., `{'report': 'text'}`).  
     - *Critical Flaw*: Uses single quotes (`'`) instead of double quotes (`"`) for JSON.

4. **Report Formatting**  
   - `ReportFormatter.format()`:  
     - Combines report title + rows (with optional uppercase).  
     - *Input*: `Report` object (title + rows).  
     - *Output*: Formatted string (e.g., `"FRUIT REPORT\napple 10\n"`).

5. **Export Pipeline**  
   - `ReportService.generate()`:  
     1. Formats report via `ReportFormatter`.  
     2. Passes formatted text to exporter's `prepare()`.  
     3. *Flaw*: Rebuilds string character-by-character (inefficient):  
        ```python
        buffer = ""
        for ch in prepared:  # ❌ O(n²) due to string concatenation
            buffer += ch
        self.exporter.export(buffer)  # Could use `prepared` directly
        ```
     4. Calls `export()` on the buffer (not `prepared`).

6. **Export Manager**  
   - `ExportManager.create_exporter()`:  
     - Maps `CONFIG["export_format"]` to exporter:  
       - `"text"` → `TextExporter` or `UpperTextExporter` (based on `uppercase`).  
       - `"json"` → `JsonLikeExporter`.  
     - *Edge Case*: Unknown format defaults to `TextExporter`.

7. **Application Flow**  
   - `Application.execute()`:  
     1. Creates `Report` instance.  
     2. Runs `ExportManager.run()`.  
     3. Records report title in history.

---

### Key Issues & Risks

| Category          | Issue                                                                 | Severity |
|-------------------|-----------------------------------------------------------------------|----------|
| **Design**        | Global `CONFIG` (breaks testability, hard to extend).                  | ⚠️⚠️⚠️    |
| **Data Integrity**| `JsonLikeExporter` returns invalid JSON (single quotes instead of double). | ⚠️⚠️⚠️    |
| **Performance**   | O(n²) string concatenation in `ReportService.generate()`.              | ⚠️⚠️      |
| **Unused Code**   | `finish()`, `after_export()`, and `retry` are never used.              | ⚠️        |
| **Edge Cases**    | `export_format` != `"text"`/`"json"` defaults to `TextExporter` (no error). | ⚠️        |

---

### Improvements

1. **Fix JSON Exporter**  
   - *Rationale*: Invalid JSON breaks consumers.  
   - *Fix*: Use `json.dumps()` for valid JSON.  
     ```python
     # Replace JsonLikeExporter.prepare()
     import json
     return json.dumps({"report": data})  # Valid JSON
     ```

2. **Remove Redundant String Building**  
   - *Rationale*: O(n²) inefficiency.  
   - *Fix*: Directly pass `prepared` to `export()`.  
     ```python
     # In ReportService.generate()
     self.exporter.export(prepared)  # Instead of buffer loop
     ```

3. **Replace Global Config with Dependency Injection**  
   - *Rationale*: Global state complicates testing and configuration.  
   - *Fix*: Inject config into relevant classes.  
     ```python
     class ReportFormatter:
         def __init__(self, uppercase: bool):
             self.uppercase = uppercase
     ```

4. **Remove Unused Methods**  
   - *Rationale*: Clean code, avoid confusion.  
   - *Fix*: Delete `finish()` and `after_export()`.

5. **Validate Export Format**  
   - *Rationale*: Prevent silent defaults.  
   - *Fix*: Raise `ValueError` for invalid formats.  
     ```python
     if fmt not in ["text", "json"]:
         raise ValueError(f"Invalid export format: {fmt}")
     ```

---

### Example Usage (Fixed)

```python
# Configured via dependency injection
formatter = ReportFormatter(uppercase=True)
exporter = UpperTextExporter()  # or JsonExporter()

report = Report("FRUIT REPORT", ["apple 10", "banana 5"])
formatted = formatter.format(report)
exporter.export(formatted)  # Directly uses formatted string
```

---

### Why This Matters
- **Security**: Invalid JSON could cause parsing errors in downstream systems.  
- **Maintainability**: Global config and unused code increase cognitive load.  
- **Performance**: String concatenation in loops is a classic anti-pattern.  
- **Correctness**: Valid JSON is non-negotiable for interoperability.

> **Final Note**: The system demonstrates the strategy pattern well but suffers from poor implementation details. Fixing the JSON and string handling would make it production-ready. Always prefer dependency injection over global state.