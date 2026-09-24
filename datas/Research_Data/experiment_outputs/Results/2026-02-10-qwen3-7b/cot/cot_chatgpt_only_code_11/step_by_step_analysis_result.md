### Code Smell Review & Analysis

---

#### **1. Unused Variable: `FRIEND_A` & `FRIEND_B`**  
**Issue**:  
- **Problem**: Variables declared but never used.  
- **Impact**: Redundant code, potential bugs, and poor maintainability.  

**Root Cause**:  
- Unnecessary variables declared without purpose or usage.  

**Fix**:  
- Remove unused variables or add usage context.  
**Example**:  
```python
# Original
FRIEND_A = "Alice"
FRIEND_B = "Bob"

# Improved
# Use variables only where needed
```

---

#### **2. Missing Docstring for `get_friends`**  
**Issue**:  
- **Problem**: Function lacks documentation.  
- **Impact**: Confusion about purpose and behavior.  

**Root Cause**:  
- Lack of clarity in function definitions.  

**Fix**:  
- Add docstring with purpose, parameters, and return values.  
**Example**:  
```python
def get_friends():
    """Return a list of friends."""
    pass
```

---

#### **3. Code Smell: Long Function `add_friend`**  
**Issue**:  
- **Problem**: Single function handles multiple unrelated tasks.  
- **Impact**: Hard to test, maintain, or reuse.  

**Root Cause**:  
- Poorly structured logic in one function.  

**Fix**:  
- Split into smaller, focused functions.  
**Example**:  
```python
def add_friend(user_id, name):
    """Add a friend to the database."""
    pass

def update_user(user_id, new_name):
    """Update a user's name."""
    pass
```

---

#### **4. Code Smell: Poor Naming Conventions**  
**Issue**:  
- **Problem**: Functions like `add_friend_relation` are vague.  
- **Impact**: Ambiguity in purpose.  

**Root Cause**:  
- Lack of descriptive names.  

**Fix**:  
- Use clear, explicit names.  
**Example**:  
```python
def add_friend_relationship(user_id, friend_id):
    """Add a friend relationship between users."""
```

---

#### **5. Code Smell: Tight Coupling**  
**Issue**:  
- **Problem**: `get_friends` relies on `FRIEND_A`/`FRIEND_B`.  
- **Impact**: Fragile and hard to test.  

**Root Cause**:  
- Logic is tightly coupled to specific variables.  

**Fix**:  
- Extract logic into helper classes or functions.  
**Example**:  
```python
class FriendManager:
    def get_friends(self):
        """Return a list of friends."""
        pass
```

---

#### **6. Code Smell: Missing Documentation**  
**Issue**:  
- **Problem**: Most functions lack comments or docstrings.  
- **Impact**: Reduced readability and maintainability.  

**Root Cause**:  
- Lack of inline or external documentation.  

**Fix**:  
- Add docstrings and inline comments.  
**Example**:  
```python
def get_unique_ages_sorted(ages):
    """Return sorted unique ages from a list."""
    return sorted(set(ages))
```

---

### Summary of Key Fixes  
| Smell Type | Priority | Impact | Fix |
|------------|----------|--------|-----|
| Unused Var | High | High | Remove or use. |
| Missing Doc | Medium | Medium | Add docstrings. |
| Long Function | High | High | Split into smaller functions. |
| Poor Naming | Medium | Medium | Use descriptive names. |
| Tight Coupling | Medium | Medium | Extract logic into helpers. |
| Missing Comments | Medium | Medium | Add comments and docstrings. |

---

### Best Practice Note  
- **SOLID Principle**: Keep functions focused and loosely coupled.  
- **DRY Principle**: Avoid repetition in code and documentation.