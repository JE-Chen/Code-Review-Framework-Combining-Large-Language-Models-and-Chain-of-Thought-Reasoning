### Code Smell Type: Global State Dependency
**Problem Location**:  
```python
DATA_STORE = []
USER_COUNT = 0
CONFIG = {"mode": "test", "threshold": 123}
```

**Detailed Explanation**:  
Using global variables violates encapsulation and introduces tight coupling. The state (`DATA_STORE`, `USER_COUNT`, `CONFIG`) is mutable across all requests, causing:
- Unpredictable behavior in concurrent environments (e.g., race conditions during `USER_COUNT += 1`).
- Impossible unit testing without global state setup.
- Hidden dependencies making code harder to reason about.

**Improvement Suggestions**:  
Replace globals with dependency injection:
```python
class DataStore:
    def __init__(self):
        self.items = []
        self.user_count = 0
        self.config = {"mode": "test", "threshold": 123}

# In route handlers, pass DataStore instance:
@app.route("/add", methods=["POST"])
def add_item(data_store: DataStore):
    item = request.json.get("item")
    data_store.items.append(item)
    data_store.user_count += 1
    return jsonify({"status": "ok", "count": data_store.user_count})
```

**Priority Level**: High

---

### Code Smell Type: Magic Numbers
**Problem Location**:  
```python
if len(item) > CONFIG["threshold"]:  # 123 is magic
if int(param) > 100:                # 100 is magic
if int(param) % 2 == 0:             # 2 is magic
```

**Detailed Explanation**:  
Hardcoded numbers lack context, increasing maintenance risks:
- Changing thresholds requires searching for all occurrences.
- Numbers like `100` and `2` are unclear without comments.
- Violates "explicit over implicit" principle.

**Improvement Suggestions**:  
Define constants with descriptive names:
```python
MAX_ITEM_LENGTH = 123
MAX_NUMBER_THRESHOLD = 100

# Usage:
if len(item) > MAX_ITEM_LENGTH:
if int(param) > MAX_NUMBER_THRESHOLD:
if int(param) % 2 == 0:  # 2 is mathematically clear, but add comment if non-obvious
```

**Priority Level**: Medium

---

### Code Smell Type: Inconsistent Return Types
**Problem Location**:  
```python
@app.route("/complex", methods=["GET"])
def complex_route():
    # Returns string instead of JSON
    if int(param) > 100:
        return "Large number"  # ❌ String
    else:
        return "Even number"   # ❌ String
```

**Detailed Explanation**:  
Mixed return types (JSON vs. raw strings) confuse clients:
- Clients expect consistent JSON responses (as in `/add` and `/items`).
- Raw strings break API contracts and require manual parsing.

**Improvement Suggestions**:  
Return JSON consistently:
```python
return jsonify({"result": "Large number"})
return jsonify({"result": "Even number"})
```

**Priority Level**: Medium

---

### Code Smell Type: Unnecessary Global Mutation
**Problem Location**:  
```python
@app.route("/reset", methods=["POST"])
def reset_data():
    CONFIG["mode"] = "reset"  # ❌ Unrelated state mutation
```

**Detailed Explanation**:  
Changing `CONFIG["mode"]` to `"reset"` is:
- Meaningless (unused elsewhere).
- Creates hidden side effects.
- Contradicts configuration immutability.

**Improvement Suggestions**:  
Remove the mutation. If needed for logging, use a separate state tracker:
```python
# Remove CONFIG["mode"] = "reset"
return jsonify({"status": "reset done"})
```

**Priority Level**: Medium

---

### Code Smell Type: Poor Input Validation
**Problem Location**:  
```python
@app.route("/add", methods=["POST"])
def add_item():
    item = request.json.get("item")  # ❌ Accepts None if missing
    DATA_STORE.append(item)  # Appends None on missing "item"
```

**Detailed Explanation**:  
Missing validation causes silent failures:
- Client might omit `"item"` by mistake.
- `None` values pollute the data store.
- No error response for invalid payloads.

**Improvement Suggestions**:  
Validate required fields:
```python
if not item:
    return jsonify({"error": "Missing 'item' in JSON"}), 400
```

**Priority Level**: Medium

---

### Code Smell Type: Nested Conditionals
**Problem Location**:  
```python
def complex_route():
    param = request.args.get("param", "")
    if param:
        if param.isdigit():
            if int(param) > 100:
                return "Large number"
            else:
                if int(param) % 2 == 0:
                    return "Even number"
                else:
                    return "Odd number"
        else:
            if param == "hello":
                return "Greeting detected"
            else:
                return "Unknown string"
    else:
        return "No parameter provided"
```

**Detailed Explanation**:  
Deep nesting reduces readability:
- Hard to follow logic flow.
- Increases cognitive load for maintenance.
- Prone to errors (e.g., missing edge cases).

**Improvement Suggestions**:  
Flatten with early returns:
```python
param = request.args.get("param", "")
if not param:
    return jsonify({"error": "No parameter provided"})

if not param.isdigit():
    return jsonify({"result": "Greeting detected"}) if param == "hello" else jsonify({"result": "Unknown string"})

num = int(param)
if num > 100:
    return jsonify({"result": "Large number"})
return jsonify({"result": "Even number"}) if num % 2 == 0 else jsonify({"result": "Odd number"})
```

**Priority Level**: Medium

---

### Code Smell Type: Misleading Naming
**Problem Location**:  
`USER_COUNT` (counts items, not users).

**Detailed Explanation**:  
Name implies user count, but actually tracks item additions:
- Causes confusion during maintenance.
- Violates semantic clarity.

**Improvement Suggestions**:  
Rename to `ITEM_COUNT`:
```python
ITEM_COUNT = 0  # Replaces USER_COUNT
```

**Priority Level**: Medium