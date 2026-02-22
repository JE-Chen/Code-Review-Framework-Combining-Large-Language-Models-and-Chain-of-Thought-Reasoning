### 1. **Global Mutable State**
**Issue**: Using `GLOBAL_STATE` directly in multiple functions makes testing and modularity difficult.
- **Explanation**: Functions rely on a shared, mutable global variable, which leads to unpredictable behavior and tight coupling.
- **Why It Happens**: Instead of managing state explicitly or through objects, the code assumes global access.
- **Impact**: Harder to reason about changes, harder to test in isolation.
- **Fix**: Encapsulate `GLOBAL_STATE` into a class or pass it as an argument.
```python
# Before
def increment_counter():
    GLOBAL_STATE['counter'] += 1

# After
class StateManager:
    def __init__(self):
        self.counter = 0

    def increment_counter(self):
        self.counter += 1
```
- **Best Practice**: Prefer dependency injection over global access.

---

### 2. **Inline Logic**
**Issue**: Complex conditionals are embedded within core logic.
- **Explanation**: Logic like filtering or applying rules is mixed in with execution flow.
- **Why It Happens**: Lack of abstraction or helper functions.
- **Impact**: Makes unit testing harder and code less reusable.
- **Fix**: Extract logic into named helper functions.
```python
# Before
if item % 2 == 0 and item > threshold:
    ...

# After
def is_valid_item(item, threshold):
    return item % 2 == 0 and item > threshold
```
- **Best Practice**: Separate concerns and extract conditional logic.

---

### 3. **Hardcoded Threshold Value**
**Issue**: A magic number used without explanation.
- **Explanation**: The value isn't explained or reused elsewhere.
- **Why It Happens**: Quick implementation without naming conventions.
- **Impact**: Less maintainable if threshold needs adjustment.
- **Fix**: Replace with a named constant.
```python
# Before
if item > 5:

# After
THRESHOLD = 5
if item > THRESHOLD:
```
- **Best Practice**: Avoid magic numbers; name important values clearly.

---

### 4. **Duplicated Code Access**
**Issue**: Repeatedly accessing keys from `GLOBAL_STATE`.
- **Explanation**: Redundant access increases risk of typos and inconsistency.
- **Why It Happens**: No caching or abstraction layer around state access.
- **Impact**: Maintenance overhead and error-prone updates.
- **Fix**: Cache values locally when used frequently.
```python
# Before
value = GLOBAL_STATE['data']
...
value = GLOBAL_STATE['data']

# After
data = GLOBAL_STATE['data']
...
data = GLOBAL_STATE['data']
```
- **Best Practice**: Reduce repetition by caching or centralizing access.

---

### 5. **Print Inside Core Logic**
**Issue**: Outputting directly inside functions rather than returning data.
- **Explanation**: Makes output hard to control or mock during tests.
- **Why It Happens**: Mixing side effects with computation.
- **Impact**: Limits flexibility in how results are handled.
- **Fix**: Return values instead of printing them.
```python
# Before
print(result)

# After
return result
```
- **Best Practice**: Core logic should be pure—output should happen at higher levels.

---