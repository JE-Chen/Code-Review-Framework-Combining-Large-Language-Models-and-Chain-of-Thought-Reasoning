## PR Summary Template

### Summary Rules
- **Key changes**: Refactor functions to avoid shared mutable state and improve readability.
- **Impact scope**: Affects all functions dealing with lists and direct input mutation.
- **Purpose of changes**: Enhance code safety, readability, and testability.
- **Risks and considerations**: Potential impact on existing functions relying on shared state.
- **Items to confirm**:
  - Verify that all functions now adhere to immutability principles where applicable.
  - Confirm that no unintended side effects exist due to changes.

### Code Diff to Review

```python
def add_item(item, container=None):
    if container is None:
        container = []
    container.append(item)
    return container

shared_list = []

def append_global(value):
    global shared_list
    shared_list.append(value)
    return shared_list

def mutate_input(data):
    return [x * 2 for x in data]

def nested_conditions(x):
    if x > 0:
        if x < 10:
            if x % 2 == 0:
                return "small even positive"
            else:
                return "small odd positive"
        else:
            if x < 100:
                return "medium positive"
            else:
                return "large positive"
    else:
        if x == 0:
            return "zero"
        else:
            return "negative"

def risky_division(a, b):
    try:
        return a / b
    except ZeroDivisionError:
        return None

def inconsistent_return(flag):
    return 42 if flag else "forty-two"

def compute_in_loop(values):
    return [v * 2 for v in values if v < len(values)]

side_effects = []
for i in range(3):
    side_effects.append(print(i))

def calculate_area(radius):
    return 3.14159 * radius * radius

def run_code(code_str):
    # Use exec instead of eval for safety
    exec(code_str)
```

### Review Points
1. **Immutability**: Ensure all functions are either pure (no side effects) or clearly documented as having side effects.
2. **Error Handling**: Verify proper error handling and exception management.
3. **Performance**: Consider whether any changes might affect performance negatively.
4. **Testing**: Ensure comprehensive unit tests cover the modified functions.