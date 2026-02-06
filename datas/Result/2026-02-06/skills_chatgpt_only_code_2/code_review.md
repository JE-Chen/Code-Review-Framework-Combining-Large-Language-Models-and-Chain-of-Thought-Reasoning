### Diff #1

---

#### **Summary**
- **Purpose**: The code loads user data from a JSON file, processes users (filtering by score, age, and activity), computes averages, identifies top users, and formats output. It includes a test harness for demonstration.
- **Affected files**: Single file (main module).
- **Plain language**: This code reads user information from a file, keeps only users who are active, scored over 60, and are 18+, then calculates their average score and finds the highest-scoring user. It also shows how to format user details for display.

---

#### **Linting Issues**
- **Redundant variable assignment**:  
  Line 37: `temp = []` followed by `temp.append(r)` is redundant. Direct iteration over `raw` is cleaner.  
  *Suggestion*: Replace with `for item in raw: ...`
  
- **Insecure file handling**:  
  Lines 19–21: Manual `open`/`close` without context manager.  
  *Suggestion*: Use `with open(DATA_FILE, "r") as f: text = f.read()`
  
- **Overly broad exception handling**:  
  Line 26: `except:` catches all exceptions (e.g., `TypeError`, `IOError`).  
  *Suggestion*: Catch specific exceptions like `json.JSONDecodeError`.
  
- **Magic number**:  
  Line 46: `u.score > 60` and `u.age >= 18` lack meaningful names.  
  *Suggestion*: Define constants (e.g., `MIN_SCORE = 60`).

- **Unused parameter**:  
  Line 56: `verbose` is unused in the main logic (only used for debug prints).  
  *Suggestion*: Remove or document its purpose.

---

#### **Code Smells**
- **Global state leakage**:  
  `_cache` is a global variable mutated by `loadAndProcessUsers`.  
  *Why problematic*: Breaks testability, causes hidden dependencies.  
  *Improvement*: Return cache explicitly or use dependency injection.

- **Inconsistent return types**:  
  `getTopUser` returns `User` or `dict` (e.g., `{"name": ..., "score": ...}` when `score > 90`).  
  *Why problematic*: Forces callers to check types (`isinstance`).  
  *Improvement*: Always return `User`, or use a dedicated `TopUser` class.

- **Overloaded function parameter**:  
  `flag=True` in `loadAndProcessUsers` overrides `active` status from the data.  
  *Why problematic*: Confusing semantics (e.g., `flag=True` means "ignore file's active status").  
  *Improvement*: Rename to `force_active=True` or split into separate functions.

- **Hardcoded file path**:  
  `DATA_FILE = "./data/users.json"`.  
  *Why problematic*: Reduces portability and testability.  
  *Improvement*: Accept `data_file` as a parameter or use environment variables.

- **Unnecessary string conversion**:  
  `avg = float(str(avg))` in `calculateAverage` (Line 78).  
  *Why problematic*: Introduces rounding errors and is redundant.  
  *Improvement*: Return `avg` directly.

- **Dead code**:  
  Lines 49–51: Commented-out `status` logic in `formatUser`.  
  *Why problematic*: Creates confusion about intentional behavior.  
  *Improvement*: Remove dead code or uncomment relevant logic.