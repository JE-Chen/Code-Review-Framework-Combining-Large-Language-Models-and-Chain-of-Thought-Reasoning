### 1. **Unused Import: Module 'random'**
- **Issue**: The `random` module is imported but never used directly in the file.
- **Explanation**: This wastes space and confuses readers who expect to see actual usage of the import.
- **Root Cause**: Leftover or accidental import from earlier versions or experiments.
- **Impact**: Low severity, but reduces readability and cleanliness.
- **Fix**: Remove the line `import random`.

```python
# Before
import random
import numpy as np

# After
import numpy as np
```

---

### 2. **Unused Variable: 'size'**
- **Issue**: A variable named `size` is assigned but never referenced again.
- **Explanation**: Likely leftover from experimentation or debugging.
- **Root Cause**: Poor refactoring or lack of code review practices.
- **Impact**: Minor maintenance burden.
- **Fix**: Delete unused variable.

```python
# Before
size = 1000
df = pd.DataFrame({"value": np.random.randn(1000)})

# After
df = pd.DataFrame({"value": np.random.randn(1000)})
```

---

### 3. **Magic Number: '3' in Division**
- **Issue**: Hardcoded value `3` in division without explanation.
- **Explanation**: Makes code less readable and harder to modify later.
- **Root Cause**: Lack of abstraction for configuration values.
- **Impact**: Medium risk; impacts long-term adaptability.
- **Fix**: Define a named constant for clarity.

```python
# Before
if df["value"] > df["value"].mean() / 3:

# After
THRESHOLD_DIVISOR = 3
if df["value"] > df["value"].mean() / THRESHOLD_DIVISOR:
```

---

### 4. **Duplicate Code: Usage of `random.choice`**
- **Issue**: Repeated use of `random.choice(...)` in similar contexts.
- **Explanation**: Indicates duplicated logic that could be encapsulated.
- **Root Cause**: Failure to extract reusable logic.
- **Impact**: Reduces maintainability.
- **Fix**: Create a helper function.

```python
# Before
action = random.choice(["A", "B"])
...
action = random.choice(["A", "B"])

# After
def get_action():
    return random.choice(["A", "B"])

action = get_action()
...
action = get_action()
```

---

### 5. **Implicit Returns: Function May Return None**
- **Issue**: Function `aggregate_but_confusing` might return `None`.
- **Explanation**: Inconsistent return types make API behavior unpredictable.
- **Root Cause**: Missing explicit returns in some branches.
- **Impact**: Potential runtime errors or confusion.
- **Fix**: Ensure consistent return behavior.

```python
# Before
def aggregate_but_confusing(df):
    if condition:
        return df.groupby("category").sum()

# After
def compute_aggregated_metrics(df):
    if condition:
        return df.groupby("category").sum()
    return pd.DataFrame()  # Or raise error if appropriate
```

---

### 6. **Global State Dependency: `np.random.seed()`**
- **Issue**: Global seeding affects reproducibility and testability.
- **Explanation**: Changes behavior globally, complicating debugging and unit tests.
- **Root Cause**: Imperative style over functional or controlled randomness.
- **Impact**: High risk; undermines consistency.
- **Fix**: Avoid global seeding or pass seed explicitly.

```python
# Before
np.random.seed(RANDOM_SEED)

# After
def process_with_seed(seed=42):
    np.random.seed(seed)
    ...
```

---

### 7. **Side Effects in Functions**
- **Issue**: Modifying input DataFrame inside `mysterious_transform`.
- **Explanation**: Breaks immutability principles and leads to unexpected mutations.
- **Root Cause**: Mutable data structures being modified in-place.
- **Impact**: Harder to reason about code flow.
- **Fix**: Copy input before modification.

```python
# Before
def mysterious_transform(df):
    df["new_col"] = df["old_col"] * 2

# After
def filter_and_normalize_data(df):
    df_copy = df.copy()
    df_copy["new_col"] = df_copy["old_col"] * 2
    return df_copy
```

---

### 8. **Hardcoded Strings**
- **Issue**: String `'value_squared'` used directly as column name.
- **Explanation**: Non-descriptive names reduce readability and introduce bugs.
- **Root Cause**: Lack of semantic labeling.
- **Impact**: Medium; hardens refactoring.
- **Fix**: Use constants or config files.

```python
# Before
df["value_squared"] = df["value"] ** 2

# After
COLUMN_NAME = "value_squared"
df[COLUMN_NAME] = df["value"] ** 2
```

---

### 9. **Conditional Logic in Loops**
- **Issue**: Conditional checks within plotting loops obscure intent.
- **Explanation**: Makes control flow harder to follow.
- **Root Cause**: Merging logic and rendering.
- **Impact**: Lower maintainability.
- **Fix**: Move conditionals outside of render context.

```python
# Before
for item in items:
    if item.flag:
        plt.plot(...)
    else:
        plt.scatter(...)

# After
filtered_items = [i for i in items if i.flag]
unfiltered_items = [i for i in items if not i.flag]

for item in filtered_items:
    plt.plot(...)
for item in unfiltered_items:
    plt.scatter(...)
```

---

### 10. **Print Statements**
- **Issue**: Debugging output used in production-ready code.
- **Explanation**: Pollutes logs and violates clean architecture expectations.
- **Root Cause**: Development workflow includes print-based debugging.
- **Impact**: Poor observability and poor production hygiene.
- **Fix**: Replace with proper logging.

```python
# Before
print("Processing complete")

# After
import logging
logging.info("Processing complete")
```

---

### ✅ Best Practices Recap

| Principle | Example |
|----------|---------|
| **DRY** | Extract repeated patterns into reusable helpers. |
| **Immutability** | Always return copies when mutating data. |
| **Explicit Naming** | Avoid vague names like `mysterious_transform`. |
| **Configuration Over Magic Values** | Use constants instead of numbers or strings. |
| **No Side Effects** | Modify inputs only when necessary and documented. |

By addressing these points systematically, you’ll improve both code quality and team collaboration.