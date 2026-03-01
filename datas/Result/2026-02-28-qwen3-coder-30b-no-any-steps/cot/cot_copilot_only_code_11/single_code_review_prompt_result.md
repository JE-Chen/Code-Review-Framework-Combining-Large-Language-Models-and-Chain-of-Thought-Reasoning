# Code Review Summary

## Strengths
- Clear separation of concerns with distinct functions
- Good use of descriptive function names
- Logical flow in main execution

## Issues & Recommendations

### 1. Global State Dependency
**Issue**: Functions directly access global `DATA` variable instead of accepting it as parameter.
```python
# Current - Bad
def calculate_average_scores():
    for user in DATA["users"]:  # Direct dependency on global

# Better
def calculate_average_scores(data):
    for user in data["users"]:  # Accepts data as parameter
```

### 2. Magic Numbers/Values
**Issue**: Hardcoded thresholds and indices.
```python
# Current - Bad
if s > 40:  # Magic number

# Better
THRESHOLD = 40
if s > THRESHOLD:
```

### 3. Inconsistent Logic Flow
**Issue**: Complex nested conditionals in main logic.
```python
# Current - Bad
if DATA["config"]["mode"] == "X":
    if DATA["config"]["flags"][0]:
        print("Mode X with flag True")
    else:
        if DATA["config"]["flags"][1]:
            print("Mode X with second flag True")
        else:
            print("Mode X with all flags False")

# Better - Use early returns or helper functions
```

### 4. Code Duplication
**Issue**: Repeated data access patterns.
```python
# Current - Bad
user["info"]["scores"]
item["value"]

# Better - Extract into helper functions
def get_user_scores(user): return user["info"]["scores"]
```

### 5. Missing Error Handling
**Issue**: No validation for missing keys or invalid data structures.
```python
# Add safety checks
if "users" in DATA and isinstance(DATA["users"], list):
    # Process users safely
```

### 6. Variable Naming
**Issue**: Vague variable names like `s`, `result`.
```python
# Current - Bad
for s in scores:

# Better
for score in scores:
```

### 7. Linter Issues
- Consider using f-strings for string formatting
- Add docstrings to functions
- Ensure consistent indentation and spacing

### 8. Testability
**Issue**: Difficult to unit test due to global dependencies.
```python
# Better approach
def main(data=DATA):
    # All functions can accept data parameter
```

### Recommendations
1. Pass data as parameters rather than relying on globals
2. Extract constants for magic values
3. Simplify complex conditional logic
4. Add defensive programming practices
5. Improve naming consistency throughout codebase