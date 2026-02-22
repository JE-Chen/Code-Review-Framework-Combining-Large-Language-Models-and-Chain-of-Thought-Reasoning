### 1. **Unused Variable (`no-unused-vars`)**
#### ✅ *Issue*
The variable `report` is reassigned but never used afterward.

#### 🧠 *Root Cause*
This usually happens during development when temporary or placeholder variables are left behind.

#### ⚠️ *Impact*
Low severity, but indicates incomplete cleanup or misunderstanding of scope.

#### 💡 *Fix*
Either remove the assignment or use the variable.

**Before:**
```python
report = "some value"
report = another_value  # unused
```

**After:**
```python
report = another_value  # only assign once
```

#### 🔑 *Best Practice*
Always review assignments before committing code.

---

### 2. **Poor Inheritance Design (`no-restricted-syntax`)**
#### ✅ *Issue*
Using `pass` in `BaseExporter.finish()` implies an unused or optional method.

#### 🧠 *Root Cause*
Methods defined in base classes may not always be applicable to child classes.

#### ⚠️ *Impact*
Violates Liskov Substitution Principle and increases maintenance cost.

#### 💡 *Fix*
Make it abstract or eliminate it entirely.

**Before:**
```python
class BaseExporter:
    def finish(self):
        pass
```

**After (abstract):**
```python
from abc import ABC, abstractmethod

class BaseExporter(ABC):
    @abstractmethod
    def finish(self):
        ...
```

#### 🔑 *Best Practice*
Only define methods in base classes that must be implemented.

---

### 3. **Unnecessary Escape Sequence (`no-unnecessary-escape`)**
#### ✅ *Issue*
String concatenation can be simplified with f-strings.

#### 🧠 *Root Cause*
Legacy style formatting still used instead of modern alternatives.

#### ⚠️ *Impact*
Readability affected slightly.

#### 💡 *Fix*
Replace with f-string or `.format()`.

**Before:**
```python
result = "{" + "'report': '" + data + "'}"  # confusing escaping
```

**After:**
```python
result = f"{{'report': '{data}'}}"
```

#### 🔑 *Best Practice*
Prefer f-strings for readability and simplicity.

---

### 4. **Duplicate Key in Dictionary (`no-duplicate-key`)**
#### ✅ *Issue*
Key `'uppercase'` appears twice in `CONFIG`.

#### 🧠 *Root Cause*
Copy-paste or oversight during configuration definition.

#### ⚠️ *Impact*
Can lead to runtime errors or silent overrides depending on Python version.

#### 💡 *Fix*
Ensure all keys are unique.

**Before:**
```python
CONFIG = {
    'uppercase': True,
    'uppercase': False,  # duplicate!
}
```

**After:**
```python
CONFIG = {
    'uppercase': False,
    'retry_count': 3,
}
```

#### 🔑 *Best Practice*
Validate configuration dictionaries at load time.

---

### 5. **Magic Number (`no-magic-numbers`)**
#### ✅ *Issue*
Hardcoded value `3` used as retry count.

#### 🧠 *Root Cause*
Constants not extracted for clarity and reuse.

#### ⚠️ *Impact*
Reduced maintainability if value needs changing later.

#### 💡 *Fix*
Define as named constant.

**Before:**
```python
RETRIES = 3
```

**After:**
```python
RETRY_COUNT = 3
```

#### 🔑 *Best Practice*
Extract constants for better documentation and reuse.

---

### 6. **Global State Usage (`no-global-state`)**
#### ✅ *Issue*
Global `CONFIG` variable accessed throughout the app.

#### 🧠 *Root Cause*
Testing becomes harder due to implicit dependencies.

#### ⚠️ *Impact*
High impact on modularity and testability.

#### 💡 *Fix*
Pass config explicitly into components.

**Before:**
```python
def process():
    return CONFIG['format']
```

**After:**
```python
def process(config):
    return config['format']
```

#### 🔑 *Best Practice*
Avoid global mutable state in favor of explicit dependencies.

---