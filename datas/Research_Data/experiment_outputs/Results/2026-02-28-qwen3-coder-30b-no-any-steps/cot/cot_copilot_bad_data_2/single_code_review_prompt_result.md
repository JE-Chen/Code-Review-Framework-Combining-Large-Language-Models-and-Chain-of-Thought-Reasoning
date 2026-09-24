## Code Review Summary

### ⚠️ Critical Issues
- **Security vulnerability**: `unsafe_eval()` function with `eval()` usage
- **Poor error handling**: Generic exception catching with no logging
- **Global state dependency**: Hardcoded global configuration affects testability

---

## 🔍 Detailed Feedback

### 1. Best Practices

**❌ Global State Dependency**
```python
# Current
global_config = {"mode": "debug"}
def run_task():
    if global_config["mode"] == "debug":
        print("Running in debug mode")
    else:
        print("Running in normal mode")
```
*Issue*: Tightly coupled to global state, makes testing difficult.
*Suggestion*: Pass configuration as parameter or use dependency injection.

**❌ Unsafe Code Execution**
```python
# Current
def unsafe_eval(user_code):
    return eval(user_code)
```
*Issue*: Security vulnerability allowing arbitrary code execution.
*Suggestion*: Remove or replace with safe alternatives like `ast.literal_eval()`.

**❌ Generic Exception Handling**
```python
# Current
def risky_update(data):
    try:
        data["count"] += 1
    except Exception:
        data["count"] = 0
    return data
```
*Issue*: Catches all exceptions without proper error handling.
*Suggestion*: Catch specific exceptions and log errors appropriately.

### 2. Linter Messages

**Naming Conventions**
- Function names like `f` and `secret_behavior` lack descriptive meaning.
- Variable `hidden_flag` is unclear; consider `is_admin_mode`.

**Unused/Dead Code**
- `timestamped_message()` function defined but never used.

### 3. Code Smells

**❌ Magic Strings**
```python
# Current
if global_config["mode"] == "debug":
```
*Issue*: String literals should be constants for maintainability.

**❌ Inconsistent Return Types**
```python
# Current
def process_user_input(user_input):
    # Returns None on invalid input, boolean otherwise
```
*Issue*: Mixed return types reduce predictability.
*Suggestion*: Standardize return types (e.g., always return boolean).

**❌ Side Effects in Pure Functions**
```python
# Current
def check_value(val):
    if val:
        return "Has value"
    else:
        return "No value"
```
*Issue*: Function has side effects through string formatting.
*Suggestion*: Separate concerns; return values and format separately.

### ✅ Strengths
- Clear separation of concerns in some functions
- Simple logic that's easy to understand
- Good use of type checking

### 🛠️ Recommendations
1. Replace `eval()` with safer alternatives
2. Improve error handling specificity
3. Use descriptive naming conventions
4. Avoid global mutable state
5. Add unit tests for edge cases