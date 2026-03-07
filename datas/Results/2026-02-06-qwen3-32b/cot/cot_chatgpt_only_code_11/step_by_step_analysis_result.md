### Code Smell & Linter Analysis Report

---

#### **1. Linter: `invalid-index-storage`**  
**Issue**: Index stored in `USER_INDEX` becomes invalid after user removals.  
**Plain English**: Storing user indices at creation time breaks when users are deleted (since list indices shift).  
**Root Cause**: Using global lists (`USER_INDEX`) instead of stable identifiers (`uid`) for lookups.  
**Impact**:  
- ❌ **Critical runtime error** (IndexError) when accessing users after removals.  
- ❌ Fragile design: Indexes must be manually updated (error-prone).  
**Fix**:  
```python
# Replace global index with uid-based lookup
user_index = {}  # uid -> current index

def add_user(uid, name, age):
    USERS.append([uid, name, age, [], {}])
    user_index[uid] = len(USERS) - 1  # Store current index

def remove_user(uid):
    idx = user_index[uid]
    del USERS[idx]
    del user_index[uid]  # Update index mapping
    # Also clean up FRIEND_A/FRIEND_B if used
```
**Best Practice**: *Never store mutable indices. Always use stable identifiers (e.g., `uid`) for data access.*

---

#### **2. Linter: `duplicate-uid`**  
**Issue**: `add_user` allows duplicate `uids`, causing inconsistent state.  
**Plain English**: Multiple users can share the same ID, leading to data corruption.  
**Root Cause**: No uniqueness check before appending to global `USERS`.  
**Impact**:  
- ❌ **Data corruption**: Friendships might link to the wrong user.  
- ❌ Silent failure (e.g., `get_friends` returns incorrect data).  
**Fix**:  
```python
def add_user(uid, name, age):
    if any(user[0] == uid for user in USERS):  # Check for duplicates
        raise ValueError(f"Duplicate uid: {uid}")
    USERS.append([uid, name, age, [], {}])
```
**Best Practice**: *Validate input uniqueness before mutation. Enforce constraints at the data layer.*

---

#### **3. Linter: `unmaintainable-data-structure`**  
**Issue**: Parallel lists `FRIEND_A`, `FRIEND_B` for friendships.  
**Plain English**: Friendship data is split across two lists, risking desync.  
**Root Cause**: Using parallel arrays instead of associative storage.  
**Impact**:  
- ❌ **High risk of inconsistency**: Adding/removing friendships may break one list.  
- ❌ Hard to debug: Must track both lists for correctness.  
**Fix**:  
```python
# Replace global lists with a dictionary
FRIENDS = {}  # uid -> [friend_id, ...]

def add_friend(uid, friend_id):
    if uid not in FRIENDS:
        FRIENDS[uid] = []
    FRIENDS[uid].append(friend_id)

def get_friends(uid):
    return FRIENDS.get(uid, [])  # No O(n) scan
```
**Best Practice**: *Prefer dictionaries/objects over parallel arrays. One source of truth per data entity.*

---

#### **4. Linter: `missing-docstring`**  
**Issue**: `create_user_record` lacks documentation.  
**Plain English**: Function purpose, parameters, and return value are unclear.  
**Root Cause**: No documentation standard enforced.  
**Impact**:  
- ❌ **Readability loss**: Developers must reverse-engineer code.  
- ❌ Higher onboarding cost for new team members.  
**Fix**:  
```python
def create_user_record(uid, name, age):
    """
    Creates a user record with default friendship data.
    
    Args:
        uid (str): Unique user identifier.
        name (str): User's full name.
        age (int): User's age.
    
    Returns:
        list: [uid, name, age, [], {}]
    """
    return [uid, name, age, [], {}]
```
**Best Practice**: *Document all public functions. Use docstrings to explain *why* and *how*.*

---

#### **5. Linter: `unsorted-unique-ages`**  
**Issue**: `get_unique_ages_sorted` returns unordered ages despite its name.  
**Plain English**: Function name implies sorted output, but it returns an unordered set.  
**Root Cause**: Misalignment between function name and implementation.  
**Impact**:  
- ❌ **Misleading behavior**: Users expect sorted results.  
- ❌ Silent bugs in downstream logic (e.g., sorting twice).  
**Fix**:  
```python
def get_unique_ages_sorted():
    unique_ages = {user[2] for user in USERS}  # Set for uniqueness
    return sorted(unique_ages)  # Explicit sort
```
**Best Practice**: *Name functions to match behavior. If sorting is required, sort it.*

---

#### **6. Linter: `dead-code`**  
**Issue**: Unused `build_age_map` function with mismatched return type.  
**Plain English**: Function exists but is never called; returns a list instead of a map.  
**Root Cause**: Unused code left behind after refactoring.  
**Impact**:  
- ❌ **Maintenance burden**: Code must be reviewed and deleted.  
- ❌ Confusion: Name suggests a map, but returns a list.  
**Fix**:  
```python
# Remove entirely (unused) or fix implementation:
def build_age_map():
    return {user[2]: user[0] for user in USERS}  # Returns dict
```
**Best Practice**: *Delete dead code. Keep the codebase lean and focused.*

---

#### **7. Linter: `negative-age`**  
**Issue**: `-1` used to mark inactive users (non-standard).  
**Plain English**: Negative ages are confusing and invalid.  
**Root Cause**: Misusing `age` field for state tracking.  
**Impact**:  
- ❌ **Confusion**: Age should always be non-negative.  
- ❌ Hard to debug: Negative values require special handling.  
**Fix**:  
```python
# Use a separate field for activity status
def create_user_record(uid, name, age, active=True):
    return [uid, name, age, [], {}, active]  # Add 'active' flag

def deactivate_user(uid):
    idx = user_index[uid]
    USERS[idx][5] = False  # Update active flag
```
**Best Practice**: *Use dedicated fields for state. Never repurpose data fields.*

---

### **Code Smell Synthesis: Global State**  
**Core Problem**: All state (`USERS`, `USER_INDEX`, etc.) is exposed globally.  
**Why It’s Bad**:  
- ❌ **Tight coupling**: Functions depend on global state.  
- ❌ **Untestable**: Requires global setup for unit tests.  
- ❌ **Non-reusable**: Cannot be plugged into other contexts.  
**Fix (High Priority)**:  
```python
class UserManager:
    def __init__(self):
        self.users = []  # Replace USERS
        self.user_index = {}  # Replace USER_INDEX
        self.friends = {}  # Replace FRIEND_A/FRIEND_B
        self.mixed_log = []  # Replace MIXED_LOG

    def add_user(self, uid, name, age):
        # ... (with duplicate check and index update)
```
**Why This Works**:  
- Encapsulates state and behavior.  
- Eliminates global dependencies.  
- Aligns with SOLID principles (Single Responsibility, Encapsulation).  

---

### **Final Recommendation**  
**Priority Order**:  
1. Replace global state with `UserManager` class (fixes *all* linter issues).  
2. Address `negative-age` and `unsorted-unique-ages` (critical for correctness).  
3. Add missing docstrings and remove dead code.  

**Prevention Strategy**:  
- Enforce code reviews for global state usage.  
- Adopt object-oriented design early.  
- Use linters to catch naming/data structure mismatches.  

> 💡 **Golden Rule**: *If a function needs global state to work, it’s a sign of poor design.* Always prefer encapsulation over global variables.