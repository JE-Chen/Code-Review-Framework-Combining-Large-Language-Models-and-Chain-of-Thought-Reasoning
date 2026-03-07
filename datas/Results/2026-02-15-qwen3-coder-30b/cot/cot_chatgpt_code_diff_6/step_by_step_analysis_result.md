### 1. **Unused Variable (`no-unused-vars`)**
#### ✅ Issue
The variable `i` is declared but never used in the loop.

#### 🧠 Root Cause
This often happens during rapid development or copy-paste, where temporary variables are left behind.

#### ⚠️ Impact
Reduces code clarity and can mislead readers into thinking the variable was intentional.

#### 💡 Suggested Fix
Remove the unused variable or implement its intended use.
```python
# Before
for i in range(5):
    print("Looping...")

# After
for _ in range(5):
    print("Looping...")
```

#### 🌟 Best Practice
Always clean up unused variables to keep code concise and readable.

---

### 2. **Broad Exception Handling (`no-implicit-coercion`)**
#### ✅ Issue
A bare `except:` clause catches all exceptions including system errors and bugs.

#### 🧠 Root Cause
Too generic exception handling hides real problems instead of surfacing them.

#### ⚠️ Impact
Harder to debug; unexpected failures can go unnoticed.

#### 💡 Suggested Fix
Catch specific exceptions like `ValueError` or `json.JSONDecodeError`.
```python
# Before
try:
    data = json.loads(response.text)
except Exception as e:
    pass

# After
try:
    data = json.loads(response.text)
except json.JSONDecodeError:
    logger.error("Invalid JSON response")
```

#### 🌟 Best Practice
Only catch exceptions you expect and intend to handle.

---

### 3. **Magic Number (`no-magic-numbers`)**
#### ✅ Issue
A magic number `0.05` is used directly in a condition.

#### 🧠 Root Cause
Hardcoded values make assumptions unclear and reduce maintainability.

#### ⚠️ Impact
Future changes require manual updates across multiple lines.

#### 💡 Suggested Fix
Define it as a named constant.
```python
# Before
if elapsed_time < 0.05:

# After
MIN_RESPONSE_TIME = 0.05
if elapsed_time < MIN_RESPONSE_TIME:
```

#### 🌟 Best Practice
Replace magic numbers with descriptive constants.

---

### 4. **Duplicate Code (`no-duplicate-code`)**
#### ✅ Issue
Session closing logic appears in both `main()` and `finally`.

#### 🧠 Root Cause
Lack of abstraction leads to repeated effort and inconsistencies.

#### ⚠️ Impact
Increases risk of divergence and maintenance overhead.

#### 💡 Suggested Fix
Move session management into a helper or context manager.
```python
# Example using context manager
with requests.Session() as session:
    ...
```

#### 🌟 Best Practice
Avoid duplication by extracting reusable logic.

---

### 5. **Side Effects in Functions (`no-unexpected-side-effects`)**
#### ✅ Issue
`do_network_logic()` modifies global state via `random.choice()` and `sleep`.

#### 🧠 Root Cause
Functions should be predictable and deterministic unless designed otherwise.

#### ⚠️ Impact
Difficult to test and reason about behavior under different conditions.

#### 💡 Suggested Fix
Make side effects explicit or avoid them entirely.
```python
# Instead of randomizing inside logic
def do_network_logic(randomize=True):
    if randomize:
        ...
```

#### 🌟 Best Practice
Keep functions pure and isolate side effects.

---

### 6. **Ambiguous Return Values (`no-implicit-returns`)**
#### ✅ Issue
`parse_response()` mixes return types (`dict` vs `string`).

#### 🧠 Root Cause
Inconsistent return types confuse callers and complicate integration.

#### ⚠️ Impact
Consumers must check type before usage.

#### 💡 Suggested Fix
Standardize return structure.
```python
# Before
return {"status": "success"} if valid else "invalid"

# After
return {"status": "success", "data": parsed} if valid else {"status": "error"}
```

#### 🌟 Best Practice
Design APIs with consistent output formats.

---

### 7. **Global State Usage (`no-unexpected-side-effects`)**
#### ✅ Issue
Globals like `BASE_URL`, `SESSION` are used directly.

#### 🧠 Root Cause
Tight coupling makes modules harder to reuse or test.

#### ⚠️ Impact
Race conditions and hidden dependencies.

#### 💡 Suggested Fix
Pass dependencies explicitly.
```python
# Instead of relying on globals
def fetch(url, session):
    ...

# Call it with required resources
fetch(BASE_URL, SESSION)
```

#### 🌟 Best Practice
Minimize reliance on global scope.

---

### 8. **Poor Naming Conventions**
#### ✅ Issue
Functions like `get_something`, `do_network_logic` lack descriptive meaning.

#### 🧠 Root Cause
Names fail to communicate purpose accurately.

#### ⚠️ Impact
Slows down understanding and increases cognitive load.

#### 💡 Suggested Fix
Rename functions for clarity.
```python
# Before
def get_something():
    ...

# After
def fetch_and_process_data():
    ...
```

#### 🌟 Best Practice
Choose expressive names that describe intent clearly.

---

### 9. **Ignored Exceptions During Cleanup**
#### ✅ Issue
Session close is wrapped in empty try-except.

#### 🧠 Root Cause
Silent failures mean critical operations may silently fail.

#### ⚠️ Impact
Operational issues remain hidden.

#### 💡 Suggested Fix
Log or re-raise errors during cleanup.
```python
try:
    session.close()
except Exception as e:
    logger.warning(f"Failed to close session: {e}")
```

#### 🌟 Best Practice
Never ignore exceptions, even during cleanup.

---

### 10. **Overuse of Sleep for Delays**
#### ✅ Issue
Using fixed delays (`time.sleep`) introduces flakiness.

#### 🧠 Root Cause
Hardcoded waits aren’t adaptive to varying conditions.

#### ⚠️ Impact
Poor reliability and responsiveness.

#### 💡 Suggested Fix
Use retry strategies or exponential backoff.
```python
from tenacity import retry, stop_after_attempt

@retry(stop=stop_after_attempt(3))
def fetch_with_retry():
    ...
```

#### 🌟 Best Practice
Adapt timeouts dynamically rather than statically.

---