---

### **Diff #1**

---

#### **1. Summary**

- This PR introduces a basic user management system with data loading, filtering, averaging, and display logic.
- The core functionality includes reading JSON-formatted user data (`users.json`), filtering active users with scores over 60 and age ≥18, calculating average scores, identifying top scorers, and printing formatted output.
- A global `_cache` is used to store the last processed list of users.
- Affected components:
  - Class: `User`
  - Functions: `loadAndProcessUsers`, `calculateAverage`, `getTopUser`, `formatUser`, `mainProcess`
  - File: `./data/users.json`

> *In simpler terms:* It loads a list of people from a file, filters them based on criteria, calculates their average score, finds the best-performing person, and prints it out.

---

#### **2. Linting Issues**

- **Missing type hints**: No function signatures include parameter or return types.
- **Unnecessary casting**: Using `float(str(avg))` after division is redundant.
- **Hardcoded paths**: `DATA_FILE = "./data/users.json"` could be made configurable or more robust.
- **Poor error handling**: Catching all exceptions during JSON parsing without logging or re-raising.
- **Redundant temporary variable**: `temp = []` followed by appending items to it is unnecessary.
- **Global state usage**: `_cache` being mutated globally can make testing harder.

> *Suggested fixes*:
> - Add type hints like `-> List[User]`.
> - Replace `float(str(avg))` with direct float conversion.
> - Use `pathlib.Path` for better path handling.
> - Log errors when JSON parsing fails instead of silently defaulting to empty list.

---

#### **3. Code Smells**

- **Tight Coupling**: The code relies heavily on hardcoded assumptions about data structure and global variables.
- **Long Functionality**: `loadAndProcessUsers()` does too many things: file I/O, JSON parsing, filtering, caching — violates single-responsibility principle.
- **Magic Numbers/Strings**: Hardcoded thresholds like `60`, `18`, `90`, `0.7` should be constants.
- **Duplication**: Similar logic exists in both `getTopUser` and `formatUser`.
- **Global State Pollution**: Global `_cache` makes behavior unpredictable and hard to test.

> *Recommendations*:
> - Split `loadAndProcessUsers()` into smaller functions (e.g., read, parse, filter).
> - Extract constants into module-level or config constants.
> - Avoid global mutable state; pass dependencies explicitly.
> - Refactor repeated conditionals or formatting logic.

---