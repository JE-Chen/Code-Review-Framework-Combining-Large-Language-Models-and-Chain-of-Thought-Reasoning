### 1. **Magic Number (`no-magic-numbers`)**
- **Issue**: The number `3.14159` is hardcoded directly in the code.
- **Explanation**: Using magic numbers reduces readability and maintainability. If you need to change the value (e.g., for higher precision), it must be updated in every place it's used.
- **Root Cause**: Lack of abstraction for constants like π.
- **Impact**: Makes code harder to update and understand.
- **Fix Suggestion**:
  Replace with `math.pi` for clarity and accuracy.
  ```python
  import math

  def calculate_area(radius):
      return math.pi * radius * radius
  ```
- **Best Practice**: Define named constants for values that are not obvious or could change.

---

### 2. **Unsafe Use of `eval()` (`no-unsafe-eval`)**
- **Issue**: The `eval()` function is being used to execute code dynamically.
- **Explanation**: This can lead to serious security vulnerabilities such as code injection if untrusted input is passed into it.
- **Root Cause**: Using `eval()` without sanitization or validation.
- **Impact**: Potential remote code execution and system compromise.
- **Fix Suggestion**:
  Avoid `eval()` entirely. For literal evaluation, use `ast.literal_eval()`. For complex parsing, build a safer parser.
  ```python
  import ast

  def safe_eval(expression):
      try:
          return ast.literal_eval(expression)
      except (ValueError, SyntaxError):
          raise ValueError("Invalid expression")
  ```
- **Best Practice**: Never allow user input to dictate executable code.

---

### 3. **Global Variable Assignment (`no-global-assign`)**
- **Issue**: Modifying a global variable inside a function affects external state unpredictably.
- **Explanation**: This breaks encapsulation and makes functions harder to test and reason about.
- **Root Cause**: Direct modification of global state rather than passing parameters or returning values.
- **Impact**: Leads to unpredictable behavior and tight coupling between components.
- **Fix Suggestion**:
  Pass `shared_list` as a parameter or encapsulate it in a class.
  ```python
  def append_global(value, container):
      container.append(value)
      return container
  ```
- **Best Practice**: Minimize reliance on global state; prefer local or scoped variables.

---

### 4. **Side Effects in List Comprehension (`no-duplicate-key`)**
- **Issue**: A list comprehension performs an I/O operation (`print()`), causing side effects.
- **Explanation**: List comprehensions should produce new lists, not trigger actions. Mixing side effects with data transformation reduces clarity.
- **Root Cause**: Misuse of list comprehensions for non-data tasks.
- **Impact**: Confuses readers and breaks functional programming principles.
- **Fix Suggestion**:
  Move `print()` outside of the comprehension.
  ```python
  for i in range(3):
      print(i)
  ```
- **Best Practice**: Keep list comprehensions focused on transformations, not actions.

---

### 5. **Inconsistent Return Types (`no-implicit-coercion`)**
- **Issue**: Function returns either an integer or a string based on a condition.
- **Explanation**: Inconsistent return types make the function unpredictable and harder to integrate into larger systems.
- **Root Cause**: No explicit decision on return type consistency.
- **Impact**: Increases risk of runtime errors and reduces API reliability.
- **Fix Suggestion**:
  Standardize return types (either all integers or all strings).
  ```python
  def consistent_return(flag):
      if flag:
          return 42
      else:
          return 42  # or str(42) if needed
  ```
- **Best Practice**: Always ensure consistent return types in functions.

---

### 6. **Deeply Nested Conditionals (`no-nested-conditional`)**
- **Issue**: Multiple levels of nested `if` statements reduce readability.
- **Explanation**: Deep nesting makes understanding control flow more difficult and prone to mistakes.
- **Root Cause**: Complex logic not broken down into smaller, manageable parts.
- **Impact**: Harder to maintain, debug, and extend.
- **Fix Suggestion**:
  Refactor using early returns or helper functions.
  ```python
  def nested_conditions(x):
      if x > 0:
          if x < 10:
              return "small even positive" if x % 2 == 0 else "small odd positive"
          elif x < 100:
              return "medium positive"
          else:
              return "large positive"
      elif x == 0:
          return "zero"
      else:
          return "negative"
  ```
- **Best Practice**: Flatten nested logic using early returns or guard clauses.

---

### 7. **Mutable Default Argument (`no-undefined-var`)**
- **Issue**: Default argument `container=[]` causes shared mutable state.
- **Explanation**: Since default arguments are evaluated once at function definition, changes persist across calls.
- **Root Cause**: Incorrect use of mutable defaults in function signatures.
- **Impact**: Unexpected behavior due to shared state between function calls.
- **Fix Suggestion**:
  Use `None` and initialize inside the function.
  ```python
  def add_item(item, container=None):
      if container is None:
          container = []
      container.append(item)
      return container
  ```
- **Best Practice**: Never use mutable objects as default arguments.

---

### 8. **Broad Exception Handling (`no-exception-raised`)**
- **Issue**: Catching `Exception` catches all possible errors, masking real problems.
- **Explanation**: This hides bugs and prevents proper error recovery.
- **Root Cause**: Overgeneralized exception handling.
- **Impact**: Makes debugging harder and can hide critical failures.
- **Fix Suggestion**:
  Catch specific exceptions like `ZeroDivisionError`.
  ```python
  def risky_division(a, b):
      try:
          return a / b
      except ZeroDivisionError:
          return None
  ```
- **Best Practice**: Only catch exceptions you intend to handle.

---

### 9. **Redundant Loop Logic (`no-loop-func`)**
- **Issue**: Loop condition compares against `len(values)` unnecessarily.
- **Explanation**: When iterating over a list, comparing index with length is redundant and confusing.
- **Root Cause**: Misunderstanding of iteration vs. indexing.
- **Impact**: Can mislead developers and introduce subtle bugs.
- **Fix Suggestion**:
  Remove unnecessary condition or clarify intent.
  ```python
  def compute_in_loop(values):
      results = []
      for v in values:
          results.append(v * 2)
      return results
  ```
- **Best Practice**: Ensure loop logic reflects clear intent—avoid redundant comparisons.

---