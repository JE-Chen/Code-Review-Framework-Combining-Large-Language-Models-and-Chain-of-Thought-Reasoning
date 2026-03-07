### Diff #1

#### **Summary**
This diff introduces multiple functions with fundamental design flaws that violate core Python best practices. The changes focus on adding utility functions but prioritize convenience over correctness and maintainability. Key issues include mutable default arguments, global state mutation, inconsistent return types, and dangerous constructs like `eval`. The code is intended for basic data manipulation but risks causing subtle bugs and security vulnerabilities. Non-experts would see inconsistent behavior (e.g., `inconsistent_return` returning integers or strings) and unexpected side effects (e.g., `add_item` altering a shared list).

---

#### **Linting Issues**
- **Mutable Default Argument**: `add_item` uses `container=[]` as a default.  
  *Violation*: Defaults evaluated once at definition time, causing shared state across calls.  
  *Fix*: Use `None` and initialize inside the function:  
  ```python
  def add_item(item, container=None):
      container = container or []
      container.append(item)
      return container
  ```

- **List Comprehension for Side Effects**: `side_effects = [print(i) for i in range(3)]`  
  *Violation*: Intended for building collections, not executing logic.  
  *Fix*: Replace with explicit loop:  
  ```python
  [print(i) for i in range(3)]  # or just `for i in range(3): print(i)`
  ```

- **Overly Broad Exception Handling**: `risky_division` catches `Exception`.  
  *Violation*: Masks all errors (e.g., `KeyboardInterrupt`), making debugging impossible.  
  *Fix*: Catch specific exceptions:  
  ```python
  try:
      return a / b
  except ZeroDivisionError:
      return None
  ```

- **Magic Number in `calculate_area`**: Hardcoded `3.14159` instead of using `math.pi`.  
  *Violation*: Reduces accuracy and readability.  
  *Fix*: Import `math` and use `math.pi`.

---

#### **Code Smells**
- **Global State Mutation**: `append_global` modifies `shared_list` without documentation.  
  *Why problematic*: Creates hidden coupling; callers cannot predict side effects.  
  *Refactor*: Remove global state. Pass state explicitly or use a class.

- **Input Mutation**: `mutate_input` alters `data` in-place.  
  *Why problematic*: Breaks the principle of least surprise; callers expect inputs to be preserved.  
  *Refactor*: Return a new list instead:  
  ```python
  def mutate_input(data):
      return [x * 2 for x in data]  # Non-destructive
  ```

- **Inconsistent Return Types**: `inconsistent_return` returns `int` or `str`.  
  *Why problematic*: Forces callers to handle multiple types, increasing error risk.  
  *Refactor*: Return consistent type (e.g., always string):  
  ```python
  return "42" if flag else "forty-two"
  ```

- **Deep Nesting in `nested_conditions`**:  
  *Why problematic*: Hard to read, test, and extend. Each condition adds cognitive load.  
  *Refactor*: Flatten with early returns or guard clauses:  
  ```python
  def nested_conditions(x):
      if x > 0:
          if x < 10:
              return "small even positive" if x % 2 == 0 else "small odd positive"
          return "medium positive" if x < 100 else "large positive"
      return "zero" if x == 0 else "negative"
  ```

- **Unnecessary Loop Work**: `compute_in_loop` computes `len(values)` on every iteration.  
  *Why problematic*: Reduces performance (O(n²) for large inputs) and confuses intent.  
  *Refactor*: Move invariant outside loop:  
  ```python
  n = len(values)
  for v in values:
      if v < n:
          results.append(v * 2)
  ```

- **Dangerous `eval` Usage**: `run_code` uses `eval(code_str)`.  
  *Why problematic*: High security risk (arbitrary code execution) and violates defense-in-depth.  
  *Refactor*: Avoid entirely; use safer alternatives like `ast.literal_eval` for trusted data.