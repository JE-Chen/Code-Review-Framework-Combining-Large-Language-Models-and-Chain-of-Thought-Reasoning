### 1. **Global State Usage (`no-global-state`)**
- **Issue:**  
  The use of a global variable `GLOBAL_CACHE` makes the code harder to test and modular.
- **Root Cause:**  
  The cache is shared across the entire application, leading to unpredictable behavior.
- **Impact:**  
  Difficult to mock or isolate during testing; risk of side effects.
- **Fix Suggestion:**  
  Pass the cache as a parameter or inject it via dependency injection.
  
  ```python
  def get_users(cache):
      # Use provided cache
      ...
  ```

---

### 2. **Generic Exception Catching (`no-raw-exceptions`)**
- **Issue:**  
  Catches `Exception` which masks specific errors.
- **Root Cause:**  
  Too broad exception handling prevents proper error diagnosis.
- **Impact:**  
  Debugging becomes harder due to loss of context.
- **Fix Suggestion:**  
  Catch more specific exceptions like `requests.RequestException`.

  ```python
  try:
      response = requests.get(url)
  except requests.RequestException as e:
      # Handle only known HTTP-related errors
      ...
  ```

---

### 3. **Duplicate Logic (`no-duplicated-logic`)**
- **Issue:**  
  Similar logic exists in `get_users`, `get_posts`, and `get_todos`.
- **Root Cause:**  
  Lack of abstraction leads to redundancy.
- **Impact:**  
  Increases maintenance burden and error-prone updates.
- **Fix Suggestion:**  
  Create a common function for fetching and caching data.

  ```python
  def fetch_and_cache(endpoint, key, cache):
      if key in cache:
          return cache[key]
      data = requests.get(endpoint).json()
      cache[key] = data
      return data
  ```

---

### 4. **Hardcoded Strings (`no-hardcoded-values`)**
- **Issue:**  
  Literal strings like `'Special User'` reduce maintainability.
- **Root Cause:**  
  Direct usage of literals without configuration management.
- **Impact:**  
  Changes require manual updates in many places.
- **Fix Suggestion:**  
  Move these into constants or config files.

  ```python
  SPECIAL_USER_MSG = "Special User"
  ```

---

### 5. **Unvalidated Input (`no-unvalidated-input`)**
- **Issue:**  
  Direct access to JSON fields without checking validity.
- **Root Cause:**  
  Assumptions about incoming data structure.
- **Impact:**  
  Potential runtime crashes or incorrect processing.
- **Fix Suggestion:**  
  Validate expected keys and types before use.

  ```python
  if 'name' in user and isinstance(user['name'], str):
      ...
  ```

---

### 6. **Magic Numbers (`no-magic-numbers`)**
- **Issue:**  
  Numbers like `5` and `20` appear without explanation.
- **Root Cause:**  
  Implicit meaning behind numeric thresholds.
- **Impact:**  
  Confusing behavior for other developers.
- **Fix Suggestion:**  
  Replace with named constants.

  ```python
  MIN_USERS_THRESHOLD = 5
  MAX_POSTS_ALLOWED = 20
  ```