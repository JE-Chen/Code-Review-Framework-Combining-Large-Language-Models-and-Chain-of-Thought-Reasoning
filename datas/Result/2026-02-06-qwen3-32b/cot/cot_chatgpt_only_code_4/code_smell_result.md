### Code Smell Type: Global Configuration Usage
**Problem Location**:  
`CONFIG` dictionary used throughout code (e.g., `ExportManager.create_exporter`, `ReportFormatter.format`, `ReportService.generate`).  
**Detailed Explanation**:  
Global mutable state creates tight coupling, complicates testing, and risks inconsistent behavior. Changing `CONFIG` mid-execution (e.g., in `main()`) breaks encapsulation and leads to hidden dependencies. For example, `ReportFormatter` relies on `CONFIG["uppercase"]` without clear context.  
**Improvement Suggestions**:  
Replace global `CONFIG` with dependency injection. Define a `Config` class with immutable properties:  
```python
class Config:
    def __init__(self, export_format="text", uppercase=False, retry=3):
        self.export_format = export_format
        self.uppercase = uppercase
        self.retry = retry

# Inject Config into relevant classes:
class ExportManager:
    def __init__(self, config: Config):
        self.config = config
        self.history = []
```
**Priority Level**: High  

---

### Code Smell Type: Insecure String Construction
**Problem Location**:  
`JsonLikeExporter.prepare` method: `"{'report': '" + data + "'}"`.  
**Detailed Explanation**:  
Unescaped user data (`data`) risks injection vulnerabilities. Single quotes break format validity (e.g., if `data` contains `'`, the string becomes invalid). This violates security best practices and data integrity.  
**Improvement Suggestions**:  
Use proper JSON serialization (valid format + escaping):  
```python
import json
class JsonExporter(BaseExporter):  # Renamed for accuracy
    def prepare(self, data):
        return json.dumps({"report": data})  # Correctly escapes data
```
**Priority Level**: High  

---

### Code Smell Type: Misleading Class Name
**Problem Location**:  
`JsonLikeExporter` class name vs. implementation.  
**Detailed Explanation**:  
The name implies JSON output, but the implementation uses single quotes and lacks escaping. This misleads developers about the output format, causing confusion and potential bugs.  
**Improvement Suggestions**:  
Rename to `CustomFormatExporter` or fix implementation to produce valid JSON. If the format is intentionally non-JSON, rename to `StringFormatExporter` and document the format.  
**Priority Level**: Medium  

---

### Code Smell Type: Tight Coupling to Global Config
**Problem Location**:  
`ReportFormatter.format` uses `CONFIG["uppercase"]` directly.  
**Detailed Explanation**:  
`ReportFormatter` depends on global state instead of receiving configuration. This prevents unit testing (e.g., testing `uppercase=True` requires modifying global state) and couples unrelated logic.  
**Improvement Suggestions**:  
Inject `uppercase` into `ReportFormatter`:  
```python
class ReportFormatter:
    def __init__(self, uppercase=False):
        self.uppercase = uppercase
    
    def format(self, report):
        text = "\n".join(r.upper() if self.uppercase else r for r in report.rows)
        return f"{report.title}\n{text}"
```
**Priority Level**: High  

---

### Code Smell Type: Variable Shadowing
**Problem Location**:  
`ReportService.generate`: `report = content` reassigns parameter.  
**Detailed Explanation**:  
Shadows the `report` parameter with a new value (`content`), breaking readability and increasing confusion (e.g., later code expects `report` to be the original `Report` object).  
**Improvement Suggestions**:  
Rename the reassigned variable:  
```python
formatted_content = formatter.format(report)
prepared = self.exporter.prepare(formatted_content)
```
**Priority Level**: Medium  

---

### Code Smell Type: Unnecessary Loop
**Problem Location**:  
`ReportService.generate`: Loop copying `prepared` to `buffer`.  
**Detailed Explanation**:  
The loop redundantly copies `prepared` (a string) into `buffer` without modification. This wastes CPU cycles and obscures intent.  
**Improvement Suggestions**:  
Replace loop with direct usage:  
```python
self.exporter.export(prepared)  # Remove buffer loop
```
**Priority Level**: Low  

---

### Code Smell Type: Unused Method
**Problem Location**:  
`BaseExporter.finish` and its implementations (e.g., `TextExporter.finish`).  
**Detailed Explanation**:  
The `finish` method is never called in the codebase (e.g., `ReportService` never invokes it). Dead code increases cognitive load and maintenance burden.  
**Improvement Suggestions**:  
Remove `finish` from `BaseExporter` and all subclasses.  
**Priority Level**: Low  

---

### Summary of Critical Issues
| Priority | Smell                          | Impact                                  |
|----------|--------------------------------|-----------------------------------------|
| High     | Global Config Usage            | Breaks encapsulation, security risks    |
| High     | Insecure String Construction   | Potential injection vulnerabilities     |
| High     | Tight Coupling to Global Config| Hinders testability and maintainability  |
| Medium   | Misleading Class Name          | Causes developer confusion              |
| Medium   | Variable Shadowing             | Reduces readability and increases bugs   |
| Low      | Unnecessary Loop               | Minor performance waste                 |
| Low      | Unused Method                  | Clutters codebase                       |