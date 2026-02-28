### 1. **Global Variable Assignment (`no-global-assign`)**
**Issue:**  
The code modifies a global variable `GLOBAL_DF`, which breaks modularity and makes testing difficult.

**Root Cause:**  
Using global variables introduces tight coupling between functions and creates hidden dependencies. Functions rely on external state instead of explicit parameters or return values.

**Impact:**  
This can lead to unpredictable behavior, difficulty in unit testing, and reduced maintainability. Changes to `GLOBAL_DF` in one place can unexpectedly affect other parts of the code.

**Fix Suggestion:**  
Pass data as function arguments and return results explicitly.

```python
# Before
def functionThatDoesTooMuchAndIsNotClear():
    GLOBAL_DF['score'] = random.randint(0, 10)

# After
def functionThatDoesTooMuchAndIsNotClear(df):
    df['score'] = random.randint(0, 10)
    return df
```

**Best Practice Tip:**  
Avoid global variables. Prefer encapsulation via parameters and return values.

---

### 2. **Unused Global Variable (`no-unused-vars`)**
**Issue:**  
The global variable `ANOTHER_GLOBAL` is declared but never used.

**Root Cause:**  
Unnecessary declarations clutter the namespace and indicate dead code.

**Impact:**  
It confuses readers and increases cognitive load without providing value.

**Fix Suggestion:**  
Delete unused variables.

```python
# Remove this line entirely
ANOTHER_GLOBAL = 42
```

**Best Practice Tip:**  
Keep code clean by removing unused code elements.

---

### 3. **Function Too Long (`function-max-lines`)**
**Issue:**  
Function `functionThatDoesTooMuchAndIsNotClear` does too many things and exceeds recommended length.

**Root Cause:**  
Violates the Single Responsibility Principle (SRP). The function tries to do everything — generate data, compute stats, print output, etc.

**Impact:**  
Harder to debug, test, and modify. Any small change risks breaking unrelated parts.

**Fix Suggestion:**  
Split into multiple smaller functions, each doing one task.

```python
def create_dataframe():
    # Generate initial DataFrame
    pass

def add_scores(df):
    # Add score column
    pass

def display_results(df):
    # Print summary
    pass
```

**Best Practice Tip:**  
Each function should have a single, well-defined responsibility.

---

### 4. **Magic Numbers (`no-magic-numbers`)**
**Issue:**  
Numbers like `20` and `50` appear directly in logic without explanation.

**Root Cause:**  
Hardcoded numbers reduce readability and flexibility.

**Impact:**  
If requirements change, locating all instances becomes tedious and error-prone.

**Fix Suggestion:**  
Replace with named constants.

```python
MIN_AGE = 20
MAX_AGE = 50

if age < MIN_AGE or age > MAX_AGE:
    ...
```

**Best Practice Tip:**  
Use descriptive constants instead of magic numbers.

---

### 5. **Poor Exception Handling (`no-bad-exception-handling`)**
**Issue:**  
Generic `except Exception as e:` is used, masking potential bugs.

**Root Cause:**  
Catching all exceptions prevents proper diagnosis and handling.

**Impact:**  
Silent failures and poor debugging experience in production.

**Fix Suggestion:**  
Catch specific exceptions or at least log the actual error.

```python
# Instead of:
try:
    risky_operation()
except Exception as e:
    print("I don't care what went wrong:", e)

# Do this:
try:
    risky_operation()
except ValueError as ve:
    logger.error(f"ValueError occurred: {ve}")
except KeyError as ke:
    logger.error(f"KeyError occurred: {ke}")
```

**Best Practice Tip:**  
Log or re-raise exceptions properly for better diagnostics.

---

### 6. **Duplicated Code (`no-duplicated-code`)**
**Issue:**  
Same logic for adding random scores appears twice with slight variations.

**Root Cause:**  
Code duplication increases risk of inconsistencies and makes future updates harder.

**Impact:**  
Changes must be applied in multiple places, increasing chance of bugs.

**Fix Suggestion:**  
Create a reusable helper function.

```python
def add_random_score(df):
    df['score'] = random.randint(0, 10)
    return df

# Then call it wherever needed
add_random_score(GLOBAL_DF)
```

**Best Practice Tip:**  
Follow DRY (Don’t Repeat Yourself) principle.

---

### 7. **Use of Global Keyword (`no-unscoped-variables`)**
**Issue:**  
The use of `global` keyword signals poor design and tight coupling.

**Root Cause:**  
Functions depend on global state, reducing predictability and testability.

**Impact:**  
Makes it harder to reason about code and leads to side effects.

**Fix Suggestion:**  
Avoid global state by passing inputs and returning outputs.

```python
# Instead of:
def update_global_df():
    global GLOBAL_DF
    GLOBAL_DF = ...

# Do:
def process_df(df):
    # Process df
    return updated_df
```

**Best Practice Tip:**  
Minimize global scope to enhance modularity.

---

### 8. **Unclear Function Naming (`naming-convention`)**
**Issue:**  
Function name `functionThatDoesTooMuchAndIsNotClear` is overly verbose and unclear.

**Root Cause:**  
Names should reflect purpose and be concise yet descriptive.

**Impact:**  
Confuses developers trying to understand the codebase.

**Fix Suggestion:**  
Rename to something clear and actionable.

```python
# Before
def functionThatDoesTooMuchAndIsNotClear():

# After
def analyze_age_and_scores(df):
    ...
```

**Best Practice Tip:**  
Use descriptive, short names that describe what the function does.

---