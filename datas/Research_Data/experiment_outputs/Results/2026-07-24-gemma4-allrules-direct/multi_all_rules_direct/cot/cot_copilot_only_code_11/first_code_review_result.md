### Code Review

**Logic & Correctness**
* **Potential Division by Zero**: In `calculate_average_scores`, if a user has an empty `scores` list, `total / len(scores)` will raise a `ZeroDivisionError`. Add a check for empty lists.

**Software Engineering Standards**
* **Tight Coupling (Global State)**: All functions depend directly on the global `DATA` object. This makes the code difficult to test and reuse. Pass the data as an argument to each function (e.g., `def calculate_average_scores(users):`).
* **Redundant Logic**: In `calculate_average_scores`, the manual loop to sum scores can be replaced with the built-in `sum()` function for better readability and performance.

**Readability & Complexity**
* **Deeply Nested Conditionals**: 
    * `process_misc` uses nested `if/else` blocks to determine labels. This can be simplified using a mapping or by determining "Large/Small" and "Even/Odd" independently.
    * `main` contains deeply nested logic for checking `config["mode"]` and `flags`. Use guard clauses or a flatter structure to reduce cognitive load.

**Naming Conventions**
* **Vague Variable Names**: In `calculate_average_scores`, the variable `s` should be renamed to `score` for clarity.

**Suggested Improvements**
* **Refactor `calculate_average_scores`**:
  ```python
  def calculate_average_scores(users):
      results = []
      for user in users:
          scores = user["info"]["scores"]
          avg = sum(scores) / len(scores) if scores else 0
          results.append({"id": user["id"], "avg": avg})
      return results
  ```
* **Refactor `process_misc`**:
  ```python
  def process_misc(misc, threshold):
      result = {}
      for item in misc:
          size = "Large" if item["value"] > threshold else "Small"
          parity = "Even" if item["value"] % 2 == 0 else "Odd"
          result[item["key"]] = f"{size} {parity}"
      return result
  ```