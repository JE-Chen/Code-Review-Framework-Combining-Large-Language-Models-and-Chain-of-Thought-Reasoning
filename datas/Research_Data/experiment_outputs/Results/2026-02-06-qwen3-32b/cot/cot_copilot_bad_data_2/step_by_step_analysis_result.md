### Code Quality Review Report

---

#### **1. I/O Operation in Business Logic (Line 3)**  
**Issue**:  
The `print` statement in `process_user_input` violates separation of concerns by mixing output logic with business rules.  

**Root Cause**:  
The function is designed to validate input and grant access, but directly prints messages instead of returning structured data.  

**Impact**:  
- ❌ **Untestable**: Unit tests cannot verify logic without mocking stdout.  
- ❌ **Inflexible**: Caller cannot customize output (e.g., logging vs. UI).  
- ⚠️ **Risk**: Unexpected I/O during tests causes flaky failures.  

**Fix**:  
Return data instead of printing:  
```python
def process_user_input(user_input):
    if not isinstance(user_input, str):
        return {"status": "error", "message": "Invalid input"}
    return {"status": "granted" if "admin" in user_input else "denied"}
```

**Best Practice**:  
*Separate concerns*: Keep business logic pure (no I/O). Handle output in a dedicated presentation layer.

---

#### **2. I/O Operation in Business Logic (Line 6)**  
**Issue**:  
`print("Access granted")` couples business logic to output.  

**Root Cause**:  
Same as above—output operations are embedded in validation logic.  

**Impact**:  
- ❌ **Test Fragility**: Tests fail if `print` is accidentally omitted.  
- ⚠️ **Readability**: Business rules obscured by side effects.  

**Fix**:  
Same as Step 1. Replace all `print` with structured return values.  

**Best Practice**:  
*Pure functions*: Avoid side effects; return data, not output.

---

#### **3. I/O Operation in Business Logic (Line 9)**  
**Issue**:  
`print("Access denied")` repeats the I/O smell.  

**Root Cause**:  
Function violates Single Responsibility Principle (SRP).  

**Impact**:  
- ❌ **Duplication**: Output logic repeated across branches.  
- ⚠️ **Maintenance**: Changing output requires modifying core logic.  

**Fix**:  
Same as Steps 1–2. Return unified status objects.  

**Best Practice**:  
*SRP*: A function should have one clear purpose (validate input, not output).

---

#### **4. Global State Dependency (Line 14)**  
**Issue**:  
`secret_behavior` depends on global `hidden_flag` instead of explicit parameters.  

**Root Cause**:  
Hidden coupling via global state makes behavior unpredictable.  

**Impact**:  
- ❌ **Non-Deterministic**: Behavior changes without function input.  
- ❌ **Untestable**: Requires global setup to test.  
- ⚠️ **Refactoring Risk**: Hard to isolate or change logic.  

**Fix**:  
Pass state explicitly:  
```python
def secret_behavior(x, use_double=False):
    return x * 2 if use_double else x + 2
```

**Best Practice**:  
*Dependency Injection*: Prefer parameters over globals for clarity and testability.

---

#### **5. Implicit Truthiness Check (Line 20)**  
**Issue**:  
`if val:` relies on implicit truthiness (e.g., `0` or `""` would return "Has value").  

**Root Cause**:  
Ambiguous condition ignores edge cases (e.g., `val=0` is truthy).  

**Impact**:  
- ❌ **Bugs**: Unexpected results (e.g., `check_value(0)` returns "Has value").  
- ⚠️ **Maintainability**: Requires deep knowledge of Python truthiness.  

**Fix**:  
Use explicit checks:  
```python
def check_value(val):
    return "Has value" if val is not None and val != "" else "No value"
```

**Best Practice**:  
*Explicit Conditions*: Avoid implicit truthiness; validate expected types/values.

---

#### **6. Non-Descriptive Function Name (Line 25)**  
**Issue**:  
`f(x)` is meaningless and obscures intent.  

**Root Cause**:  
Poor naming violates readability conventions.  

**Impact**:  
- ❌ **Confusion**: Unclear purpose (e.g., why multiply by 7?).
- ⚠️ **Maintenance**: Hard to refactor or understand later.  

**Fix**:  
Rename to describe purpose:  
```python
def calculate_discount(price):
    return price * 0.7 + 13  # 30% off + $13 fixed
```

**Best Practice**:  
*Naming*: Functions should read like sentences (e.g., `calculate_discount`).

---

#### **7. Global State Dependency (Line 32)**  
**Issue**:  
`run_task` relies on global `global_config` instead of parameters.  

**Root Cause**:  
Global state creates hidden dependencies.  

**Impact**:  
- ❌ **Test Isolation**: Tests require global setup.  
- ⚠️ **Debugging Complexity**: Behavior changes without function signature change.  

**Fix**:  
Inject configuration:  
```python
def run_task(config):
    return config["max_retries"] * 2
```

**Best Practice**:  
*Explicit Dependencies*: Functions should declare all inputs.

---

#### **8. Time-Dependent Logic (Line 38)**  
**Issue**:  
`timestamped_message` uses `time.time()` directly, breaking test determinism.  

**Root Cause**:  
Hard-coded system time dependency.  

**Impact**:  
- ❌ **Non-Deterministic Tests**: Test outputs vary between runs.  
- ⚠️ **Mocking Difficulty**: Requires complex test setup.  

**Fix**:  
Inject time source:  
```python
def timestamped_message(msg, now=time.time):
    return f"{now()} - {msg}"
```

**Best Practice**:  
*Dependency Injection for Time*: Mock time sources in tests.

---

#### **9. Dangerous `eval` Usage (Line 41)**  
**Issue**:  
`unsafe_eval` uses `eval()`, risking remote code execution.  

**Root Cause**:  
Arbitrary code execution from untrusted input.  

**Impact**:  
- 🔥 **Critical Security Risk**: Allows attackers to run malicious code.  
- ❌ **Unpredictable Behavior**: Input directly controls execution.  

**Fix**:  
Replace with safe alternatives:  
```python
import ast
def safe_eval(user_code):
    return ast.literal_eval(user_code)  # Only parses literals (e.g., numbers, strings)
```

**Best Practice**:  
*Avoid Dynamic Code Execution*: Never use `eval()` with user input.

---

#### **10. Input Mutation (Line 46)**  
**Issue**:  
`risky_update` mutates input `data` without documentation.  

**Root Cause**:  
Hidden side effect (modifying caller’s object).  

**Impact**:  
- ❌ **Surprise Side Effects**: Caller’s data altered unexpectedly.  
- ⚠️ **Debugging Nightmare**: Hard to trace origin of changes.  

**Fix**:  
Return new object instead of mutating:  
```python
def risky_update(data):
    updated = data.copy()
    try:
        updated["count"] += 1
    except KeyError:
        updated["count"] = 0
    return updated
```

**Best Practice**:  
*Immutable Inputs*: Preserve caller’s data; return new objects.

---

### Summary of Critical Issues  
| Priority | Issue                          | Risk Level |  
|----------|--------------------------------|------------|  
| High     | I/O in business logic          | 🔥 Security/Reliability |  
| High     | Global state dependency        | 🔥 Testability |  
| High     | `eval()` usage                 | 🔥 Critical Security |  
| Medium   | Implicit truthiness            | ⚠️ Logic Bugs |  
| Medium   | Time-dependent logic           | ⚠️ Test Stability |  
| Low      | Non-descriptive function name  | ⚠️ Readability |