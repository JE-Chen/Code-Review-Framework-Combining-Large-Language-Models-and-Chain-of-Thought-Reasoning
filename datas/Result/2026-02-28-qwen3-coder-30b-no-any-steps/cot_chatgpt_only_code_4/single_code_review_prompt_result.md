# Code Review Summary

## 1. Linting Issues

- **Naming Convention Violations**: 
  - Class names `BaseExporter`, `TextExporter`, etc., should follow PascalCase but are correctly named.
  - Variable `fmt` in `create_exporter()` could be more descriptive like `format_type`.

- **Style Violations**:
  - Inconsistent indentation (mixing tabs/spaces) — not present here, but worth noting if extended.
  - Missing docstrings for public methods/classes.
  - No PEP8 compliance check performed, though formatting seems acceptable.

- **Magic Strings/Numbers**:
  - `"text"` and `"json"` used directly as keys in conditional logic instead of constants or enums.

- **Language Best Practices**:
  - Global mutable config (`CONFIG`) used throughout the application without encapsulation or immutability guarantees.

---

## 2. Code Smells

### ⚠️ **Refused Bequest**
- `BaseExporter.finish()` is implemented in base class even though many subclasses don't use it.
  - This violates Liskov Substitution Principle.

### ⚠️ **God Object – `ExportManager`**
- Contains both factory logic (`create_exporter`) and orchestration (`run`), violating Single Responsibility Principle.

### ⚠️ **Feature Envy**
- `ReportFormatter.format()` accesses `CONFIG["uppercase"]` which belongs to global context rather than being injected.

### ⚠️ **Primitive Obsession**
- Using raw strings for configuration values (`"text"`, `"json"`).
  - Should be replaced with enums or constants.

### ⚠️ **Tight Coupling**
- Direct dependency on global `CONFIG`.
- `ReportService` tightly couples with `ReportFormatter`.

### ⚠️ **Duplicated Logic**
- Loop over characters in `generate()` unnecessarily reassembles string character-by-character.

### ⚠️ **Poor Separation of Concerns**
- Business logic (`format`) mixed with presentation (`print()`).

---

## 3. Maintainability

### ❌ Readability
- Hard-to-follow flow due to tight coupling and lack of abstraction layers.

### ❌ Modularity
- Lack of clear interfaces; `BaseExporter` has unused methods.

### ❌ Reusability
- Hard-coded configurations make reuse difficult across environments.

### ❌ Testability
- Difficult to mock dependencies or isolate behavior because of global state and tight coupling.

### ⚠️ SOLID Violations
- **Liskov Substitution**: `finish()` method not required by all subtypes.
- **Open/Closed Principle**: Adding new exporters requires modifying `ExportManager`.

---

## 4. Performance Concerns

### ⚠️ Inefficient String Building
- The loop `for ch in prepared: buffer = buffer + ch` results in O(n²) complexity due to repeated string concatenation.

### ⚠️ Unnecessary Computation
- Redundant assignment: `report = content` followed immediately by usage of `prepared`.

### ⚠️ Time Measurement Overhead
- Measuring execution time but not using it meaningfully.

---

## 5. Security Risks

### ❌ Injection Vulnerabilities
- Potential SQL injection-like risks if input is not sanitized before being passed into `JsonLikeExporter`.

### ❌ Unsafe Deserialization
- JSON-like output is constructed manually without escaping or validation.

### ⚠️ Improper Input Validation
- No checks on validity of inputs (`title`, `rows`) beyond existence.

### ⚠️ Hardcoded Secrets
- While not actual secrets, hardcoding config values reduces flexibility.

---

## 6. Edge Cases & Bugs

### ⚠️ Null Handling
- No explicit handling of missing or invalid data fields (`title`, `rows`).

### ⚠️ Boundary Conditions
- If `rows` is empty, there may be unexpected output behavior.

### ⚠️ Race Conditions
- None apparent in current synchronous design, but threading implications are ignored.

### ⚠️ Unhandled Exceptions
- No try-except blocks around critical sections (e.g., file I/O or network calls).

---

## 7. Suggested Improvements

### ✅ Refactor Configuration Management
Replace global `CONFIG` with an immutable config object or injectable service.

```python
from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class ExportConfig:
    export_format: str
    uppercase: bool
    retry: int
```

### ✅ Remove Unused Methods
Remove `BaseExporter.finish()` unless intended for all subclasses.

### ✅ Encapsulate Formatting Logic
Move `uppercase` logic into a dedicated formatter or strategy pattern.

### ✅ Replace Character Loop with Efficient Join
Instead of:
```python
buffer = ""
for ch in prepared:
    buffer = buffer + ch
```
Use:
```python
buffer = ''.join(prepared)
```

### ✅ Introduce Strategy Pattern for Exporters
Avoid if/elif chains in favor of registration or factory patterns.

Example:
```python
class ExportStrategyRegistry:
    strategies = {}

    @classmethod
    def register(cls, name, strategy_class):
        cls.strategies[name] = strategy_class

    @classmethod
    def get_strategy(cls, name):
        return cls.strategies.get(name)
```

### ✅ Improve Testability
Make services accept dependencies via constructor injection rather than globals.

### ✅ Add Type Hints
For better IDE support and maintainability:
```python
def generate(self, report: Report) -> None:
```

---

## Summary of Critical Fixes Needed

| Area | Issue | Recommendation |
|------|-------|----------------|
| Architecture | God object `ExportManager` | Split into factory + executor roles |
| Design | Tight coupling with global config | Inject config or environment |
| Performance | String concatenation in loop | Use `''.join()` |
| Maintainability | Feature envy in `ReportFormatter` | Move logic closer to data |
| Testing | Difficult to test isolated units | Dependency injection |

These changes will improve robustness, readability, and scalability of the system.