### Code Smell Type: Long Parameter List
**Problem Location**:  
```python
def doSomething(a, b, c, d, e, f, g, h, i, j):
```

**Detailed Explanation**:  
The function has 10 parameters, violating readability and maintainability principles. Long parameter lists indicate the function is handling too many responsibilities, making it hard to understand, test, and modify. Parameters lack semantic grouping (e.g., unrelated values like `a` and `e` are mixed), increasing cognitive load for callers. This also prevents future refactoring without breaking all callers.

**Improvement Suggestions**:  
- Group related parameters into a data structure (e.g., `InputParams` class or dictionary).  
- Split into focused functions (e.g., `calculate_arithmetic`, `handle_string_conditions`).  
- Example refactor:  
  ```python
  class CalculationParams:
      def __init__(self, a, b, c, d, e, f, g, h, i, j):
          self.a, self.b, self.c, self.d, self.e, self.f, self.g, self.h, self.i, self.j = a, b, c, d, e, f, g, h, i, j

  def doSomething(params: CalculationParams) -> int:
      # Logic using params.a, params.b, etc.
  ```

**Priority Level**: High  

---

### Code Smell Type: Deeply Nested Conditionals
**Problem Location**:  
```python
if a > 10:
    if b < 5:
        if c == 3:
            if d != 0:
                result = (a * b * c) / d
            else:
                result = 999999
        else:
            result = a + b + c + d
    else:
        if e == "yes":
            result = len(e) * 1234
        else:
            result = 42
else:
    if f == "no":
        result = 123456789
    else:
        result = -1
```

**Detailed Explanation**:  
4 levels of nesting in `doSomething` and similar structure in `main` reduce readability and increase error risk. Deep nesting often stems from unrefactored logic, making it hard to add new conditions or debug. The RAG rule explicitly prohibits this, as it "increases cognitive load" and "indicates the function is doing too much." The `y` condition in `main` suffers from the same issue.

**Improvement Suggestions**:  
- Use **guard clauses** to flatten conditionals:  
  ```python
  def doSomething(params):
      if params.a <= 10:
          return 123456789 if params.f == "no" else -1
      if params.b >= 5:
          return 42 if params.e != "yes" else len(params.e) * 1234
      if params.c != 3:
          return params.a + params.b + params.c + params.d
      return (params.a * params.b * params.c) / params.d if params.d != 0 else 999999
  ```
- Extract business logic to helper functions (e.g., `is_arithmetic_case`, `is_string_case`).

**Priority Level**: High  

---

### Code Smell Type: Global Variable
**Problem Location**:  
```python
dataList = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]  # Global

def processData():
    x = 0
    for k in range(len(dataList)):  # Depends on global
        # ...
```

**Detailed Explanation**:  
`dataList` is a global variable, violating encapsulation. This couples `processData` to external state, making it non-reusable and impossible to test in isolation. Changes to `dataList` anywhere in the codebase could break unrelated logic. RAG rules state: "Be cautious with shared mutable state... make behavior difficult to reason about or test."

**Improvement Suggestions**:  
- Pass data explicitly as a parameter:  
  ```python
  def processData(data: list) -> int:
      x = 0
      for value in data:
          x += value * 2 if value % 2 == 0 else value * 3
      return x
  ```
- Call with: `print("Process:", processData([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]))`.

**Priority Level**: High  

---

### Code Smell Type: Magic Numbers
**Problem Location**:  
```python
result = 999999  # Error placeholder
result = len(e) * 1234  # Arbitrary multiplier
result = 123456789  # Hardcoded value
```

**Detailed Explanation**:  
Numbers like `999999`, `1234`, and `123456789` lack context, making the code opaque. They’re prone to errors (e.g., `123456789` might be misremembered as `1234567`), and changes require hunting through code. RAG rules mandate replacing these with named constants for clarity.

**Improvement Suggestions**:  
- Define constants with descriptive names:  
  ```python
  ERROR_VALUE = 999999
  STRING_MULTIPLIER = 1234
  MAX_PROCESS_VALUE = 123456789
  ```
- Use constants consistently:  
  ```python
  result = ERROR_VALUE if d == 0 else (a * b * c) / d
  ```

**Priority Level**: Medium  

---

### Code Smell Type: Multiple Return Points
**Problem Location**:  
`doSomething` has 5 distinct return paths (e.g., `result = 999999`, `result = 42`, etc.).

**Detailed Explanation**:  
Multiple return statements fragment the logic, complicating flow tracking and testing. The RAG rule states: "Functions and methods should have a single, clear responsibility." Returning from every branch makes it hard to verify all paths and violates the principle of predictable behavior.

**Improvement Suggestions**:  
- Assign results to a single variable and return once:  
  ```python
  result = -1  # Default
  if a > 10:
      if b < 5:
          if c == 3:
              result = (a * b * c) / d if d != 0 else ERROR_VALUE
          else:
              result = a + b + c + d
      else:
          result = STRING_MULTIPLIER * len(e) if e == "yes" else 42
  else:
      result = MAX_PROCESS_VALUE if f == "no" else -1
  return result
  ```

**Priority Level**: Medium  

---

### Code Smell Type: Violation of Single Responsibility Principle
**Problem Location**:  
`doSomething` handles arithmetic, string validation, condition branching, and error handling.

**Detailed Explanation**:  
The function does too much, violating the core principle of separation of concerns. This makes it brittle (e.g., changing arithmetic logic breaks string handling) and untestable (requires mocking 10 parameters). RAG rules emphasize: "Functions should have a single, clear responsibility."

**Improvement Suggestions**:  
- Split into specialized functions:  
  ```python
  def calculate_arithmetic(a, b, c, d):
      return (a * b * c) / d if d != 0 else ERROR_VALUE

  def handle_string(e):
      return len(e) * STRING_MULTIPLIER if e == "yes" else 42
  ```
- Refactor `doSomething` to orchestrate these:  
  ```python
  def doSomething(a, b, c, d, e, f):
      if a > 10 and b < 5 and c == 3:
          return calculate_arithmetic(a, b, c, d)
      if a > 10 and e == "yes":
          return handle_string(e)
      # ... other branches
  ```

**Priority Level**: High