### 1. **No Global Variables (`no-global-variables`)**
- **Issue**: The global variable `GLOBAL_CACHE` reduces modularity and testability.
- **Explanation**: Using a global cache makes the functions dependent on shared state, which complicates unit testing and makes it hard to reason about code behavior.
- **Why It Happens**: Global variables introduce tight coupling between components.
- **Impact**: Makes code harder to test, debug, and reuse in different contexts.
- **Fix**: Pass cache as a parameter or encapsulate caching logic in a class.
  ```python
  def get_users(client, cache=None):
      if cache is None:
          cache = {}
      ...
  ```

---

### 2. **Unused Variable (`no-unused-vars`)**
- **Issue**: Variable `r` in the main loop is unused.
- **Explanation**: The variable `r` is only used for printing but never actually processed or returned.
- **Why It Happens**: Likely leftover from debugging or copy-paste.
- **Impact**: Confusing for readers; reduces code clarity.
- **Fix**: Remove unused variable or refactor to use it meaningfully.
  ```python
  # Before
  for r in results:
      print(r)

  # After
  for item in results:
      print(item)
  ```

---

### 3. **Duplicate Code (`no-duplicate-code`)**
- **Issue**: Functions `get_users`, `get_posts`, and `get_todos` have nearly identical logic.
- **Explanation**: Each function performs the same steps—fetch data, update cache, return results.
- **Why It Happens**: Lack of abstraction leads to repetition.
- **Impact**: Difficult to maintain and extend when logic needs updating.
- **Fix**: Extract common logic into a generic function.
  ```python
  def fetch_endpoint(client, endpoint, cache):
      if endpoint in cache:
          return cache[endpoint]
      response = client.fetch(endpoint)
      cache[endpoint] = response
      return response
  ```

---

### 4. **Implicit Exception Handling (`no-implicit-exception-handling`)**
- **Issue**: Catches all exceptions (`except Exception as e:`).
- **Explanation**: This catches everything including system-level errors, masking real bugs.
- **Why It Happens**: Lazy error handling due to lack of specificity.
- **Impact**: Makes debugging harder and can hide critical runtime issues.
- **Fix**: Catch specific exceptions like `requests.RequestException`.
  ```python
  except requests.RequestException as e:
      print(f"Request failed: {e}")
  ```

---

### 5. **Hardcoded Values (`no-hardcoded-values`)**
- **Issue**: Hardcoded strings like `'Special User:'` and `'Long Post:'`.
- **Explanation**: These literals should be constants to avoid duplication and improve consistency.
- **Why It Happens**: Direct use of magic strings without abstraction.
- **Impact**: Maintenance overhead; changes require updates in multiple locations.
- **Fix**: Define them as module-level constants.
  ```python
  SPECIAL_USER_PREFIX = "Special User:"
  LONG_POST_PREFIX = "Long Post:"
  ```

---

### 6. **Magic Numbers (`no-magic-numbers`)**
- **Issue**: Magic numbers `5` and `20` appear directly in logic.
- **Explanation**: Unnamed numeric thresholds reduce readability and flexibility.
- **Why It Happens**: Numeric literals used without context.
- **Impact**: Difficult to understand intent and modify later.
- **Fix**: Replace with named constants.
  ```python
  MIN_RESULTS_THRESHOLD = 5
  MAX_RESULTS_THRESHOLD = 20
  ```

---

### 7. **Side Effects in Functions (`no-side-effects-in-functions`)**
- **Issue**: Functions modify `GLOBAL_CACHE`, creating side effects.
- **Explanation**: Side effects make functions unpredictable and harder to test.
- **Why It Happens**: Not following functional principles—functions shouldn’t alter external state.
- **Impact**: Leads to brittle code and race conditions.
- **Fix**: Return data and let caller manage caching.
  ```python
  def get_users(client):
      response = client.fetch("/users")
      return response  # No modification of cache here
  ```

---

### 8. **Unneeded Else Block (`no-unneeded-else`)**
- **Issue**: Nested if/else blocks reduce readability.
- **Explanation**: Complex nesting can obscure control flow.
- **Why It Happens**: Poor structuring of conditional logic.
- **Impact**: Harder to read and maintain.
- **Fix**: Simplify with early returns or `elif`.
  ```python
  # Before
  if count > 5:
      if count < 20:
          print("Medium")
      else:
          print("High")
  else:
      print("Low")

  # After
  if count <= 5:
      print("Low")
  elif count <= 20:
      print("Medium")
  else:
      print("High")
  ```

---