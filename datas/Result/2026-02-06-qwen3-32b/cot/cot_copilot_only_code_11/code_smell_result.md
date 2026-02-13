### Code Smell Type: Global Variable Usage
- **Problem Location**:  
  All functions (`calculate_average_scores`, `filter_high_scores`, `process_misc`, `main`) directly access `DATA` global variable.
- **Detailed Explanation**:  
  Hardcoding data dependencies via global variables creates tight coupling, making code untestable in isolation. Functions become state-dependent, violating the Single Responsibility Principle. Refactoring would require passing `DATA` as an argument or injecting dependencies, enabling unit testing and modular reuse. This also increases risk of unintended side effects when `DATA` is modified elsewhere.
- **Improvement Suggestions**:  
  Replace global `DATA` with dependency injection. For example:  
  ```python
  def calculate_average_scores(data):
      return [{"id": user["id"], "avg": sum(user["info"]["scores"]) / len(user["info"]["scores"])}
              for user in data["users"]]
  ```
  Update `main()` to pass `DATA` to functions. Use type hints for clarity.
- **Priority Level**: High

---

### Code Smell Type: Magic Numbers
- **Problem Location**:  
  Hardcoded value `40` in `filter_high_scores` and implicit threshold usage in `process_misc`.
- **Detailed Explanation**:  
  `40` lacks context (why 40? Why not `DATA["config"]["threshold"]`?). This creates inconsistency: the threshold in config is `50`, but `filter_high_scores` uses `40`. Readers must mentally reconcile these, increasing bug risk. Magic numbers hinder maintainability—changing the value requires scanning multiple locations.
- **Improvement Suggestions**:  
  Define constants or use config values explicitly:  
  ```python
  HIGH_SCORE_THRESHOLD = 40  # Or use DATA["config"]["threshold"] consistently
  
  # In filter_high_scores:
  if s > HIGH_SCORE_THRESHOLD:
  ```
  Prefer consistency: use the same threshold source everywhere (e.g., always `DATA["config"]["threshold"]`).
- **Priority Level**: High

---

### Code Smell Type: Duplicate Conditional Logic
- **Problem Location**:  
  `process_misc` contains near-identical logic for even/odd values.
- **Detailed Explanation**:  
  The parity check (`value % 2 == 0`) duplicates the threshold check structure. This violates DRY (Don’t Repeat Yourself), making future changes error-prone. If threshold logic evolves, changes must be replicated in two branches. The duplicated condition also obscures intent.
- **Improvement Suggestions**:  
  Extract parity and threshold checks:  
  ```python
  def get_category(value, threshold):
      parity = "Even" if value % 2 == 0 else "Odd"
      size = "Large" if value > threshold else "Small"
      return f"{size} {parity}"
  
  # In process_misc:
  result[item["key"]] = get_category(item["value"], DATA["config"]["threshold"])
  ```
  Reduces duplication and clarifies business logic.
- **Priority Level**: Medium

---

### Code Smell Type: Deeply Nested Conditionals
- **Problem Location**:  
  `main()`’s mode handling logic (nested `if-else` for `DATA["config"]["flags"]`).
- **Detailed Explanation**:  
  The `if DATA["config"]["mode"] == "X"` block has excessive nesting (3 levels), reducing readability. This structure complicates understanding and maintenance—e.g., adding a new flag requires modifying the same deeply nested block. It also hides the core logic behind conditional complexity.
- **Improvement Suggestions**:  
  Flatten the logic using early returns or a state map:  
  ```python
  def handle_mode(mode, flags):
      if mode != "X":
          return "Other mode"
      if flags[0]:
          return "Mode X with flag True"
      if flags[1]:
          return "Mode X with second flag True"
      return "Mode X with all flags False"
  
  # In main():
  print(handle_mode(DATA["config"]["mode"], DATA["config"]["flags"]))
  ```
  Improves readability and isolates business rules.
- **Priority Level**: Medium

---

### Code Smell Type: Missing Documentation
- **Problem Location**:  
  All functions lack docstrings; global `DATA` structure is undocumented.
- **Detailed Explanation**:  
  Absence of docstrings prevents understanding function purpose, parameters, and return values. The `DATA` structure’s semantics (e.g., why `config["mode"]` is `"X"`) are unclear. This impedes onboarding and debugging, especially for new team members.
- **Improvement Suggestions**:  
  Add concise docstrings:  
  ```python
  def calculate_average_scores(data: dict) -> list:
      """Calculate average scores for each user in data['users']."""
      # ...
  
  # For DATA, add a comment above the variable:
  # DATA structure: 
  #   users: List[dict{id, name, info{age, scores}}]
  #   config: {threshold: int, mode: str, flags: List[bool]}
  ```
  Use type hints for clarity.
- **Priority Level**: Low

---

### Summary of Fixes Priority
| Code Smell                     | Priority |
|--------------------------------|----------|
| Global Variable Usage          | High     |
| Magic Numbers                  | High     |
| Duplicate Conditional Logic    | Medium   |
| Deeply Nested Conditionals     | Medium   |
| Missing Documentation          | Low      |

**Critical Path**: Fix global variables and magic numbers first (High priority) to enable testability and consistency. Then address duplication and nesting (Medium). Documentation is low-impact but recommended for long-term maintainability.