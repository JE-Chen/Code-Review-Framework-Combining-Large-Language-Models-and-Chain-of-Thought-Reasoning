### Title:  
Code Riddled with Anti-Patterns: I/O in Logic, Hidden State, and Security Risks  

### Overview:  
This code violates core software engineering principles by mixing I/O with business logic, relying on global state, using unsafe `eval`, and ignoring explicit validation. It creates testability issues, security vulnerabilities, and unpredictable behavior.  

---

### Detailed Explanation:  

#### **1. `process_user_input(user_input)`**  
- **Purpose**: Validates input and checks for "admin" substring.  
- **Flow**:  
  1. Checks if input is a string (fails for non-strings).  
  2. If input contains "admin", prints "Access granted" and returns `True`.  
  3. Otherwise, prints "Access denied" and returns `False`.  
- **Problems**:  
  - ✘ **I/O inside logic**: Prints directly instead of returning results.  
  - ✘ **Inconsistent return types**: Returns `None` on invalid input (breaks caller expectations).  
  - ✘ **No validation**: Accepts non-strings but returns `None` without context.  
- **Edge Cases**:  
  - `user_input = ""` → Returns `False` (correct, but no error message).  
  - `user_input = 123` → Returns `None` (caller might crash on `None` usage).  

---

#### **2. `secret_behavior(x)`**  
- **Purpose**: Doubles or adds 2 to input based on `hidden_flag`.  
- **Flow**:  
  - Uses global `hidden_flag` (default `True`) to determine behavior.  
- **Problems**:  
  - ✘ **Hidden dependency**: Behavior changes without explicit input.  
  - ✘ **Non-deterministic**: Calling `secret_behavior(5)` may return `10` or `7` based on external state.  
  - ✘ **Hard to test**: Requires mutating global state for tests.  

---

#### **3. `check_value(val)`**  
- **Purpose**: Checks if `val` is truthy.  
- **Flow**:  
  - Returns `"Has value"` for truthy values (e.g., `"text"`, `1`, `[1]`).  
  - Returns `"No value"` for falsy values (e.g., `""`, `0`, `None`).  
- **Problems**:  
  - ✘ **Implicit truthiness**: Fails to distinguish between `None` and empty containers.  
  - ✘ **Ambiguous names**: `val` could be `None`, `0`, or `""`—all treated the same.  
  - **Critical edge case**: `check_value(0)` returns `"Has value"` (unexpected for numeric logic).  

---

#### **4. `run_task()`**  
- **Purpose**: Prints mode based on global config.  
- **Flow**:  
  - Checks `global_config["mode"]` and prints `"debug"` or `"normal"`.  
- **Problems**:  
  - ✘ **Global state**: `global_config` can be mutated anywhere.  
  - ✘ **No return value**: Caller cannot programmatically use the result.  
  - ✘ **I/O in logic**: Prints instead of returning a value.  

---

#### **5. `unsafe_eval(user_code)`**  
- **Purpose**: Executes arbitrary code from input.  
- **Flow**:  
  - Calls `eval(user_code)`, executing the string as Python.  
- **Problems**:  
  - ✘ **Critical security risk**: Allows remote code execution (e.g., `user_code = "os.system('rm -rf /')"`).  
  - ✘ **No validation**: Accepts any input string.  

---

#### **6. `risky_update(data)`**  
- **Purpose**: Increments `data["count"]`.  
- **Flow**:  
  - Tries `data["count"] += 1`.  
  - On exception, sets `data["count"] = 0`.  
  - Returns mutated `data`.  
- **Problems**:  
  - ✘ **Input mutation**: Caller’s dictionary is modified unexpectedly.  
  - ✘ **Overly broad exception**: Catches *all* exceptions (e.g., `KeyError` for missing `"count"`).  
  - ✘ **No clear return intent**: Returns mutated object instead of new state.  

---

### Key Violations Summary:  
| Principle                          | Violated Function(s)               |  
|------------------------------------|-----------------------------------|  
| Single Responsibility              | `process_user_input`, `run_task`   |  
| Explicit Interfaces                | `secret_behavior`, `global_config` |  
| Avoid `eval`                       | `unsafe_eval`                    |  
| Explicit Truthiness                | `check_value`                    |  
| Avoid Input Mutation               | `risky_update`                   |  
| No Hidden State                    | `secret_behavior`, `run_task`      |  
| Security for External Input        | `unsafe_eval`                    |  

---

### Improvements:  

1. **Extract I/O from Logic**  
   ```python  
   def validate_input(user_input):  # Returns validation result  
       if not isinstance(user_input, str):  
           raise ValueError("Input must be a string")  
       return True  
   
   def check_admin(user_input):  # Pure business logic  
       return "admin" in user_input  
   
   # Usage:  
   try:  
       validate_input(user_input)  
       is_admin = check_admin(user_input)  
       print("Access granted" if is_admin else "Access denied")  
   except ValueError as e:  
       print(f"Error: {e}")  
   ```  
   *Rationale: Separates concerns; callers handle I/O.*  

2. **Replace Global State with Explicit Parameters**  
   ```python  
   def secret_behavior(x, hidden_flag):  # Explicit dependency  
       return x * 2 if hidden_flag else x + 2  
   ```  
   *Rationale: Eliminates hidden dependencies; enables deterministic testing.*  

3. **Remove `unsafe_eval`**  
   - **Replace with**: Safe alternatives like `ast.literal_eval` or business-specific parsers.  
   *Rationale: Prevents remote code execution attacks.*  

4. **Fix `check_value`**  
   ```python  
   def is_truthy(value):  # Explicit check  
       return bool(value)  
   ```  
   *Rationale: Avoids implicit truthiness (e.g., `is_truthy(0)` → `False`).*  

5. **Avoid Input Mutation**  
   ```python  
   def safe_update(data):  # Returns new dict  
       return {**data, "count": data.get("count", 0) + 1}  
   ```  
   *Rationale: Preserves input immutability; caller controls state.*  

---

### Why This Matters:  
- **Security**: `unsafe_eval` is a critical vulnerability (e.g., hackers could run `os.exit(0)`).  
- **Testability**: Functions like `secret_behavior` cannot be tested in isolation.  
- **Maintainability**: Hidden state (`global_config`) causes "spooky action at a distance."  
- **Edge Cases**: `check_value(0)` returns `"Has value"`—a subtle bug waiting to happen.  

> 💡 **Golden Rule**: If a function does more than one thing, split it. If it relies on hidden state, make it explicit. If it executes untrusted code, remove it.