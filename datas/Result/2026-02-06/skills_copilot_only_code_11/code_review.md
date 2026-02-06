### Diff #1

---

### Summary
- **Purpose**: Processes a global `DATA` structure to compute user score averages, filter high scores, and categorize miscellaneous values based on configuration.
- **Scope**: Affects four functions (`calculate_average_scores`, `filter_high_scores`, `process_misc`, `main`) and a global `DATA` dictionary.
- **Plain-language explanation**: This script analyzes user data (scores, ages) and config settings to generate reports. It calculates average scores per user, lists high scores (>40), categorizes misc values by parity and threshold, and prints results based on the active mode.

---

### Linting Issues
- **Magic number 40** in `filter_high_scores` (line 22):  
  `if s > 40:`  
  *Suggestion*: Replace with `HIGH_SCORE_THRESHOLD = 40` for clarity.
- **Hard-coded mode "X"** in `main` (line 34):  
  `if DATA["config"]["mode"] == "X":`  
  *Suggestion*: Define `MODE_X = "X"` at module level.
- **Unnecessary nested conditionals** in `process_misc` (lines 18-24):  
  ```python
  if item["value"] % 2 == 0:
      if item["value"] > DATA["config"]["threshold"]:
  ```  
  *Suggestion*: Flatten conditions to reduce nesting.

---

### Code Smells
- **Global state dependency** (all functions):  
  Functions rely on the global `DATA` dictionary instead of accepting it as input.  
  *Why it’s bad*: Makes code untestable (no dependency injection), prone to accidental side effects, and violates single responsibility.
  *Recommendation*: Pass `data` as a parameter to all functions (e.g., `def calculate_average_scores(data):`).

- **Magic number 50** in `config` (line 6):  
  `threshold": 50,`  
  *Why it’s bad*: Value lacks context; changes require code search.
  *Recommendation*: Define `THRESHOLD = 50` in `config` or as a top-level constant.

- **Inconsistent return structures**:  
  `filter_high_scores` returns `{"user": ..., "score": ...}` while other functions return IDs.  
  *Why it’s bad*: Creates cognitive load for consumers; mixes user names with scores.
  *Recommendation*: Return consistent structures (e.g., `{"id": ..., "score": ...}`).

- **Overly complex `main` logic** (lines 34-40):  
  Deeply nested `if`/`else` for mode handling.  
  *Why it’s bad*: Hard to extend or debug; violates the "fail fast" principle.
  *Recommendation*: Extract mode handling to a dedicated function.

- **Redundant condition in `process_misc`** (lines 18-24):  
  Checks `item["value"] % 2 == 0` twice.  
  *Why it’s bad*: Duplication increases maintenance risk.
  *Recommendation*: Simplify to:
  ```python
  parity = "Even" if item["value"] % 2 == 0 else "Odd"
  category = "Large" if item["value"] > DATA["config"]["threshold"] else "Small"
  result[item["key"]] = f"{category} {parity}"
  ```