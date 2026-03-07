## Best Practices

**Mutable Default Arguments**: The `add_item` function uses a mutable default argument (`container=[]`). This creates a shared state across calls. Each call to `add_item()` without specifying a container will use the same list instance, leading to unexpected behavior.

*Fix*: Use `None` as default and create new list inside function:
```python
def add_item(item, container=None):
    if container is None:
        container = []
    container.append(item)
    return container
```

**Side Effects in List Comprehension**: The list comprehension `[print(i) for i in range(3)]` has unwanted side effects. List comprehensions should be pure operations.

*Fix*: Separate concerns:
```python
for i in range(3):
    print(i)
```

**Global State Mutation**: `append_global` modifies global state directly, making code unpredictable and hard to test.

*Fix*: Pass dependencies explicitly or return modified values.

## Linter Messages

**Unused Variables**: `side_effects` is assigned but never used.

**Missing Docstrings**: Functions lack documentation explaining their purpose and parameters.

## Code Smells

**Deeply Nested Conditions**: `nested_conditions` has excessive nesting that reduces readability. The logic can be simplified using early returns.

*Refactor*:
```python
def nested_conditions(x):
    if x == 0:
        return "zero"
    elif x < 0:
        return "negative"
    elif x < 10:
        return "small even positive" if x % 2 == 0 else "small odd positive"
    elif x < 100:
        return "medium positive"
    else:
        return "large positive"
```

**Overly Broad Exception Handling**: `risky_division` catches all exceptions, masking potential bugs.

*Fix*: Catch specific exceptions:
```python
try:
    return a / b
except ZeroDivisionError:
    return None
```

**Inconsistent Return Types**: `inconsistent_return` returns different types based on condition, making callers unpredictable.

*Fix*: Standardize return types:
```python
def consistent_return(flag):
    if flag:
        return 42
    else:
        return 42  # or convert to string consistently
```

**Redundant Computation**: `compute_in_loop` unnecessarily recomputes `len(values)` on each iteration.

*Fix*: Cache length:
```python
def compute_in_loop(values):
    results = []
    length = len(values)  # cache length
    for v in values:
        if v < length:  # use cached value
            results.append(v * 2)
    return results
```

**Security Risk**: `run_code` uses `eval()` which executes arbitrary code and poses serious security risks.

*Fix*: Avoid dynamic code execution entirely or use safer alternatives.

## Strengths

The code demonstrates basic Python constructs and covers various programming patterns. Some functions have clear single responsibilities where possible.

## Key Improvements Needed

1. Eliminate mutable default arguments
2. Reduce nesting through early returns
3. Handle exceptions more specifically
4. Avoid side effects in expressions
5. Improve error handling and input validation
6. Document functions properly