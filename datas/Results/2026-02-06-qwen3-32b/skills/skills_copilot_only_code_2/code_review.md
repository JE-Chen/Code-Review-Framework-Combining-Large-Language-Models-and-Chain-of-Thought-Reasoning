### Diff #1

---

### **Summary**
This diff introduces a simple data processing pipeline with two specialized processors (`StringProcessor` and `NumberProcessor`) and a configurable pipeline runner (`DataPipeline`). The code demonstrates transforming input data through sequential steps (string → ASCII conversion → mathematical transformation) and uses global configuration to control behavior. Key components include:
- **Base class** (`BaseProcessor`) for polymorphic processing.
- **Specialized processors** handling specific data types.
- **Pipeline orchestration** via `DataPipeline`.
- **Global configuration** (`GLOBAL_CONFIG`) for runtime behavior.
- **Example usage** in `main()` showing string processing and conditional logging.

*Plain-language explanation*:  
This code creates a "data factory" that processes inputs through customizable steps (e.g., turning `"abc123"` into a transformed number) and uses a global settings file to change how the system behaves (like enabling "weird mode").

---

### **Linting Issues**
- **Deeply nested conditionals** (in `main`):
  ```python
  if GLOBAL_CONFIG["flag"]:
      if val > 5:
          if val < GLOBAL_CONFIG["threshold"]:
              if GLOBAL_CONFIG["mode"] == "weird":
  ```
  *Violation*: Excessive nesting (4 levels) exceeds readability best practices.  
  *Suggestion*: Refactor into guard clauses or helper functions.

- **Magic numbers** (in `NumberProcessor`):
  ```python
  return (data * 1234) % 5678 + 9999
  ```
  *Violation*: Unexplained numeric literals.  
  *Suggestion*: Replace with named constants (e.g., `TRANSFORM_FACTOR = 1234`).

---

### **Code Smells**
- **Global configuration dependency**:
  - *Issue*: `GLOBAL_CONFIG` is hardcoded and global, coupling logic to external state.
  - *Why bad*: Makes code brittle, non-testable, and error-prone (e.g., accidental config mutation).
  - *Fix*: Inject configuration via constructor (e.g., `DataPipeline(config=GLOBAL_CONFIG)`).

- **Overly complex `main()`**:
  - *Issue*: Combines pipeline setup, execution, and logging logic.
  - *Why bad*: Violates single responsibility principle; hard to modify or test.
  - *Fix*: Split into `setup_pipeline()`, `run_example()`, and `log_output()`.

- **Magic strings in conditionals**:
  - *Issue*: `"weird"` and `"mode"` used directly in `main()`.
  - *Why bad*: String literals increase maintenance risk (e.g., typos).
  - *Fix*: Define constants (e.g., `CONFIG_MODE_WEIRD = "weird"`).

- **Inefficient string concatenation** (in `StringProcessor`):
  - *Issue*: `result += ...` in a loop (O(n²) complexity).
  - *Why bad*: Poor performance for large inputs (e.g., long strings).
  - *Fix*: Use list comprehensions + `join()` (e.g., `result = ''.join([ch.upper() if ch.isalpha() else str(ord(ch)) for ch in data])`).

- **Redundant `super()` calls**:
  - *Issue*: `super().process(data)` in child classes when base class does nothing.
  - *Why bad*: Adds unnecessary complexity for minimal benefit.
  - *Fix*: Remove `super()` calls if base class is trivial (or replace with explicit fallback).