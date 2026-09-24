---

### **Diff #1**

#### **Summary**
This diff introduces several Python functions that exhibit various anti-patterns and design flaws. It includes:
- A function with a mutable default argument (`add_item`)
- A global variable mutation via `append_global`
- An input-mutating function (`mutate_input`)
- Nested conditional logic (`nested_conditions`)
- Risky exception handling (`risky_division`)
- Inconsistent return types (`inconsistent_return`)
- Side effects in list comprehension (`side_effects`)
- Dangerous usage of `eval` (`run_code`)
- Redundant computation inside a loop (`compute_in_loop`)

The changes span multiple unrelated functionalities and lack consistency in coding standards.

#### **Linting Issues**
- ❌ Mutable default argument used in `add_item()` (line 1).
  - **Fix**: Use `None` as default and initialize list inside function body.
- ❌ Side effect in list comprehension (`side_effects`) (line 18).
  - **Fix**: Replace with explicit loop like `for i in range(3): print(i)`.

#### **Code Smells**
- 🧨 **Shared mutable state**: Global `shared_list` is modified by `append_global()`.
  - **Problem**: Can cause unexpected behavior across modules or tests.
  - **Improvement**: Pass state explicitly or encapsulate in a class.
- ⚠️ **Input mutation without documentation**: `mutate_input()` modifies its input directly.
  - **Problem**: Surprising side effects for callers.
  - **Improvement**: Return a new list or document mutation clearly.
- 🔁 **Deep nesting in conditionals**: `nested_conditions()` has deeply nested `if` blocks.
  - **Problem**: Hard to read and maintain.
  - **Improvement**: Flatten logic using early returns or helper functions.
- ❗ **Too broad exception handling**: `risky_division()` catches all exceptions.
  - **Problem**: Masks real bugs; hides meaningful error messages.
  - **Improvement**: Catch specific exceptions or re-raise them.
- 🤔 **Inconsistent return types**: `inconsistent_return()` returns both `int` and `str`.
  - **Problem**: Makes caller code fragile and less predictable.
  - **Improvement**: Standardize return type or raise an exception.
- ⚠️ **Unnecessary work in loop**: `compute_in_loop()` repeats `len(values)` call.
  - **Problem**: Minor inefficiency; reduces readability.
  - **Improvement**: Cache `len(values)` outside the loop.
- 💥 **Security risk via `eval`**: `run_code()` uses `eval()` which allows arbitrary code execution.
  - **Problem**: Potential security vulnerability.
  - **Improvement**: Avoid dynamic evaluation unless absolutely necessary.

---

### ✅ Example Fixes

#### For `add_item`:
```python
def add_item(item, container=None):
    if container is None:
        container = []
    container.append(item)
    return container
```

#### For `nested_conditions`:
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

#### For `compute_in_loop`:
```python
def compute_in_loop(values):
    length = len(values)
    results = []
    for v in values:
        if v < length:
            results.append(v * 2)
    return results
```

#### For `side_effects`:
```python
for i in range(3):
    print(i)
```

#### For `risky_division`:
```python
def risky_division(a, b):
    if b == 0:
        raise ZeroDivisionError("Cannot divide by zero")
    return a / b
```

#### For `run_code`:
Avoid using `eval()` unless strictly required for specialized tools like interpreters or DSLs. If needed, sanitize input rigorously.

---