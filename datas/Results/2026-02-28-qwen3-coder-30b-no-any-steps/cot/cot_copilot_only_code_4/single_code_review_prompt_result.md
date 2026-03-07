## Linter Issues

**Missing docstrings**: Functions lack documentation explaining parameters, return values, and behavior.
```python
def risky_division(a, b):  # Missing docstring
    """Divide a by b, handling division by zero."""
```

**Inconsistent exception handling**: Mixing broad `Exception` catches with specific ones creates maintenance issues.

## Code Smells

**Magic Numbers**: Hardcoded return values (`9999`, `0`, `-1`, `-999`) make code less maintainable and harder to understand.

**Overly Broad Exception Handling**: Using generic `Exception` catches hides bugs and makes debugging difficult.

**Resource Management Issues**: Manual file closing violates Python's context manager best practices.

**Nested Try Blocks**: Deeply nested exception handling reduces readability and increases cognitive load.

## Strengths

✅ Good separation of concerns with distinct functions  
✅ Basic error handling implemented  

## Recommendations

1. **Replace magic numbers** with named constants or proper error types
2. **Use context managers** for file operations: `with open(filename, "r") as f:`
3. **Be more specific** with exception types instead of catching broad exceptions
4. **Add proper logging** instead of `print()` statements
5. **Consider returning explicit error states** rather than magic values

## Example Improvements

```python
# Instead of:
return 9999

# Use:
return float('inf')  # or raise custom exception

# Instead of:
try:
    f = open(filename, "r")
    # ...
    f.close()

# Use:
with open(filename, "r") as f:
    data = f.read()
```