### Code Quality Review Report

---

#### **1. Global Variable Usage**  
*Rule: `use-global` (Error)*  
**Issue**:  
Hardcoded reliance on global `DATA` across all functions, violating modularity and testability.  

**Root Cause**:  
Functions directly access a global variable instead of receiving data as explicit parameters. This creates tight coupling and hidden dependencies.  

**Impact**:  
- **Critical**: Code becomes untestable in isolation (e.g., unit tests require global state setup).  
- **High Risk**: Unintended side effects if `DATA` is mutated elsewhere.  
- **Maintainability**: Hard to refactor or reuse logic.  

**Suggested Fix**:  
Pass data as parameters and inject dependencies.  
```python
# BEFORE (global dependency)
def calculate_average_scores():
    return [{"id": user["id"], "avg": sum(user["info"]["scores"]) / len(user["info"]["scores"])}
            for user in DATA["users"]]

# AFTER (dependency injection)
def calculate_average_scores(data: dict) -> list:
    return [{"id": user["id"], "avg": sum(user["info"]["scores"]) / len(user["info"]["scores"])}
            for user in data["users"]]
```

**Best Practice**:  
Adhere to **Dependency Injection Principle** (SOLID). Avoid global state to enable isolation, testing, and reuse.  

---

#### **2. Missing Docstrings**  
*Rules: `missing-docstring` (Warnings)*  
**Issue**:  
All functions lack docstrings explaining purpose, inputs, and outputs.  

**Root Cause**:  
Omission of documentation during implementation, treating code as self-explanatory.  

**Impact**:  
- **High**: Slows onboarding and debugging (e.g., unclear return types).  
- **Medium**: Increases risk of misuse (e.g., wrong input types).  
- **Low**: Less severe than global variables but critical for long-term maintainability.  

**Suggested Fix**:  
Add concise docstrings with type hints.  
```python
def calculate_average_scores(data: dict) -> list:
    """
    Calculate average scores for each user in data['users'].
    
    Args:
        data: Dictionary containing 'users' list with user info.
    
    Returns:
        List of dicts with 'id' and 'avg' score.
    """
    # Implementation
```

**Best Practice**:  
Follow **Python Docstring Conventions** (e.g., NumPy style). Document *what* and *why*, not just *how*.  

---

#### **3. Misleading Function Name**  
*Rule: `misleading-name` (Warning)*  
**Issue**:  
`filter_high_scores` implies returning filtered user data, but actually returns individual scores.  

**Root Cause**:  
Name does not match implementation logic (e.g., `filter` suggests list filtering, not score extraction).  

**Impact**:  
- **Medium**: Causes confusion during code reviews or refactoring.  
- **Risk**: May lead to incorrect usage (e.g., expecting a filtered list).  

**Suggested Fix**:  
Rename to reflect actual behavior.  
```python
# BEFORE
def filter_high_scores():
    ...

# AFTER
def extract_high_scores():
    # Returns list of individual high scores
    return [s for user in DATA["users"] for s in user["info"]["scores"] if s > 40]
```

**Best Practice**:  
Use **descriptive names** aligned with function behavior (e.g., `extract_*` instead of `filter_*`).  

---

#### **4. No Empty Check**  
*Rule: `no-empty-check` (Warning)*  
**Issue**:  
`calculate_average_scores` lacks validation for empty `scores` lists, risking `ZeroDivisionError`.  

**Root Cause**:  
Assumes non-empty input without defensive checks.  

**Impact**:  
- **Medium**: Runtime failure if input is empty (e.g., empty `scores` list).  
- **Critical for Stability**: Unhandled edge cases disrupt application flow.  

**Suggested Fix**:  
Add input validation.  
```python
def calculate_average_scores(data: dict) -> list:
    # Handle empty scores safely
    return [
        {"id": user["id"], "avg": sum(user["info"]["scores"]) / len(user["info"]["scores"]) 
         if user["info"]["scores"] else 0}
        for user in data["users"]
    ]
```

**Best Practice**:  
Validate inputs early to prevent runtime errors. Follow **Defensive Programming** principles.  

---

### Priority Summary
| Issue                          | Priority | Rationale                                                                 |
|--------------------------------|----------|---------------------------------------------------------------------------|
| Global Variable Usage          | High     | Blocks testing and enables hidden bugs.                                   |
| Missing Docstrings             | Medium   | Hinders maintainability but doesn’t break functionality.                   |
| Misleading Function Name       | Medium   | Causes confusion but is fixable with a simple rename.                      |
| No Empty Check                 | Medium   | Critical edge case; risks runtime failures.                               |

**Critical Path**:  
1. Fix **global variables** (enables testing and reduces coupling).  
2. Add **empty checks** (prevents crashes).  
3. Address **docstrings** and **naming** (improves readability).  

> 💡 **Final Note**: Prioritize refactoring global state first—this unlocks testability and reduces the risk of cascading failures. Always validate inputs and document behavior explicitly.