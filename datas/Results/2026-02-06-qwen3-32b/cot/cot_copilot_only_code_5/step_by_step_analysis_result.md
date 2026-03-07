### Code Quality Review Report  

---

#### **1. Missing Docstring (Line 9)**  
**Issue**:  
Function `init_data()` lacks documentation explaining its purpose, parameters, and return value.  

**Root Cause**:  
No developer guidance is provided for how to use the function or what it does. Developers must reverse-engineer logic instead of understanding intent.  

**Impact**:  
- ❌ High risk of misuse (e.g., passing invalid arguments).  
- ❌ Slows onboarding and debugging.  
- ❌ Reduces code maintainability over time.  

**Suggested Fix**:  
Add a concise docstring.  
```python
def init_data():
    """Initialize data (1-20) and reset counter."""
    GLOBAL_STATE["data"] = [i for i in range(1, 21)]
    GLOBAL_STATE["counter"] = len(GLOBAL_STATE["data"])
```  

**Best Practice**:  
Always document functions with `Purpose`, `Parameters`, and `Return` (e.g., Google style).  

---

#### **2. Missing Docstring (Line 13)**  
**Issue**:  
Function `increment_counter()` lacks documentation.  

**Root Cause**:  
Assumes reader knows the function’s role without context.  

**Impact**:  
- ❌ Unclear if return value is *new* or *old* counter.  
- ❌ Breaks readability for new team members.  

**Suggested Fix**:  
Clarify return value.  
```python
def increment_counter():
    """Increment counter and return new value."""
    GLOBAL_STATE["counter"] += 1
    return GLOBAL_STATE["counter"]
```  

**Best Practice**:  
Document *what* the function does and *why* it matters (e.g., "returns updated counter for tracking progress").  

---

#### **3. Missing Docstring (Line 17)**  
**Issue**:  
Function `process_items()` lacks documentation.  

**Root Cause**:  
Business logic is hidden behind implementation details.  

**Impact**:  
- ❌ Critical risk: Logic may be misapplied (e.g., `flag` or `threshold` usage unclear).  
- ❌ Impossible to refactor safely without understanding.  

**Suggested Fix**:  
Explain transformation rules.  
```python
def process_items():
    """Transform items based on state:
    - If flag=True: even items doubled, odd items tripled.
    - If flag=False: items > threshold reduced by threshold, else increased.
    Returns processed list."""
    # Implementation remains unchanged
```  

**Best Practice**:  
Docstrings should enable *usage* without reading code (e.g., "Use when...").  

---

#### **4. Missing Docstring (Line 21)**  
**Issue**:  
Function `reset_state()` lacks documentation.  

**Root Cause**:  
No indication of *what* is reset or *why*.  

**Impact**:  
- ❌ Hidden side effects (e.g., resetting `mode` when unused).  
- ❌ Tests fail if reset logic changes unexpectedly.  

**Suggested Fix**:  
Clarify scope of reset.  
```python
def reset_state():
    """Reset counter, data, and flag to initial state.
    Note: 'mode' is unused and will be removed in future."""
    GLOBAL_STATE["data"] = []
    GLOBAL_STATE["counter"] = 0
    GLOBAL_STATE["flag"] = False
```  

**Best Practice**:  
Document *side effects* and *deprecation notes* in docstrings.  

---

#### **5. Missing Docstring (Line 36)**  
**Issue**:  
Function `get_threshold()` lacks documentation.  

**Root Cause**:  
Assumes reader knows the purpose of the threshold.  

**Impact**:  
- ❌ Risk of inconsistent threshold usage (e.g., `77` hardcoded elsewhere).  
- ❌ Prevents safe refactoring.  

**Suggested Fix**:  
Explain threshold’s role.  
```python
def get_threshold():
    """Return current threshold value (default: 77)."""
    return GLOBAL_STATE["threshold"]
```  

**Best Practice**:  
Reference constants *in docstrings* (e.g., "default: 77").  

---

#### **6. Missing Docstring (Line 42)**  
**Issue**:  
Function `set_threshold()` lacks documentation.  

**Root Cause**:  
No validation or usage context for `new_threshold`.  

**Impact**:  
- ❌ Potential for invalid thresholds (e.g., negative values).  
- ❌ Hard to audit threshold changes.  

**Suggested Fix**:  
Add parameter validation note.  
```python
def set_threshold(new_threshold):
    """Set threshold to new value (must be > 0)."""
    GLOBAL_STATE["threshold"] = new_threshold
```  

**Best Practice**:  
Document *constraints* for parameters (e.g., "must be positive").  

---

#### **7. Global State Abuse (Line 1)**  
**Issue**:  
`GLOBAL_STATE` is mutable global state.  

**Root Cause**:  
State is shared across functions without encapsulation.  

**Impact**:  
- ❌ **High risk**: Tests require global state setup/teardown.  
- ❌ **Critical bug risk**: `reset_state()` corrupts unused `mode`.  
- ❌ **Non-testable**: Logic cannot be isolated.  

**Suggested Fix**:  
Replace with state class.  
```python
class AppState:
    def __init__(self):
        self.counter = 0
        self.data = []
        self.flag = False
        self.threshold = 77  # Magic number resolved

    def init_data(self):
        """Initialize data (1-20) and counter."""
        self.data = list(range(1, 21))
        self.counter = len(self.data)
```  

**Best Practice**:  
Prefer **encapsulation** over global state (SOLID: *Encapsulation* principle).  

---

### Summary of Fixes  
| Issue                  | Severity | Priority | Impact of Fix                                  |
|------------------------|----------|----------|------------------------------------------------|
| Missing Docstrings     | Medium   | High     | Enables safe usage, reduces bugs.              |
| Global State Abuse     | Critical | **Highest** | Unlocks testability, removes hidden bugs.      |

**Critical Recommendation**:  
**Fix global state first** (as shown in #7). This resolves the highest-impact issues (testability, bug risk) and *enables* proper docstrings for the rest. Without this, docstrings alone won’t prevent misuse.  

> 💡 **Golden Rule**: *If you can’t write a clear docstring, refactor the code first.*  
> Example: Docstrings for `AppState` become trivial because state is encapsulated.