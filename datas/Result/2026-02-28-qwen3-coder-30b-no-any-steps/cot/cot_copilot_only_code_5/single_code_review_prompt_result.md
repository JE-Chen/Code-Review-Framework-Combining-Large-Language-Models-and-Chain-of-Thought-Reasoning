## Code Review Summary

### ⚠️ Key Issues Identified
1. **Global State Abuse**: Direct mutation of global variables makes code hard to test and reason about
2. **Magic Values**: Hardcoded values like `77` and `21` lack context or configuration
3. **Tight Coupling**: Functions depend on shared mutable state instead of explicit parameters
4. **Inconsistent Design**: Mixed imperative and functional patterns without clear boundaries

---

## 🔍 Detailed Feedback

### 🌟 Strengths
- Clear separation of concerns in function responsibilities
- Simple data processing logic with readable conditionals
- Basic state management pattern implemented

### ⚠️ Linter & Best Practice Issues

**1. Global Variable Usage**
```python
# ❌ Problem: Direct access to GLOBAL_STATE
GLOBAL_STATE["counter"] += 1

# ✅ Better: Pass state explicitly or use class-based approach
def increment_counter(state):
    state["counter"] += 1
    return state["counter"]
```

**2. Magic Numbers**
```python
# ❌ Problem: Unexplained hardcoded value
"threshold": 77

# ✅ Better: Use named constants or configuration
THRESHOLD = 77
```

**3. Implicit Dependencies**
```python
# ❌ Problem: Functions assume specific global state structure
def process_items():
    # Relies on GLOBAL_STATE["flag"] and GLOBAL_STATE["threshold"]

# ✅ Better: Accept dependencies as parameters
def process_items(data, flag, threshold):
    ...
```

### 🧼 Code Smells

**1. State Mutation Without Clear Ownership**
```python
# ❌ Problem: Multiple functions modify same global dict
def reset_state():
    GLOBAL_STATE["counter"] = 0
    GLOBAL_STATE["data"] = []
    # ... other mutations

# ✅ Better: Centralized state management
class AppState:
    def __init__(self):
        self.counter = 0
        self.data = []
        self.mode = "default"
        self.threshold = 77
        self.flag = False
```

**2. Inconsistent Return Behavior**
```python
# ❌ Problem: Some functions return values, others don't
def increment_counter():
    GLOBAL_STATE["counter"] += 1
    return GLOBAL_STATE["counter"]  # Returns new value

def reset_state():
    # No return, but mutates global state

# ✅ Better: Consistent behavior
def increment_counter():
    GLOBAL_STATE["counter"] += 1
    return GLOBAL_STATE["counter"]

def reset_state():
    GLOBAL_STATE.update({"counter": 0, "data": [], "mode": "reset", "flag": False})
    return None
```

**3. Nested Conditional Logic**
```python
# ❌ Problem: Deep nesting reduces readability
if GLOBAL_STATE["flag"]:
    if item % 2 == 0:
        ...

# ✅ Better: Early returns or clearer structure
if not GLOBAL_STATE["flag"]:
    # Handle non-flag case
    pass
else:
    # Handle flag case
    pass
```

### 💡 Recommendations

1. **Replace Global State**: Use a dedicated class or data structure for application state
2. **Parameterize Constants**: Extract magic numbers into configurable values
3. **Reduce Side Effects**: Make functions pure where possible
4. **Add Type Hints**: Improve maintainability with explicit typing
5. **Testability**: Refactor to enable unit testing without side effects

### ✅ Example Refactor
```python
from dataclasses import dataclass
from typing import List

@dataclass
class AppState:
    counter: int = 0
    data: List[int] = None
    mode: str = "default"
    threshold: int = 77
    flag: bool = False
    
    def __post_init__(self):
        if self.data is None:
            self.data = list(range(1, 21))

def process_items(state: AppState) -> List[int]:
    # Implementation using state object directly
    pass
```