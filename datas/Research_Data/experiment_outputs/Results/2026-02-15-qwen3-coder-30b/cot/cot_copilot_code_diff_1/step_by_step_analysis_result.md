### 1. **Global State Usage**
- **Issue**: Using global variables (`DATA`, `RESULTS`) makes the code harder to test and maintain.
- **Explanation**: These variables are shared across modules, increasing coupling and making it hard to isolate behavior for testing.
- **Why It Happens**: Not following dependency injection principles or encapsulation patterns.
- **Impact**: Reduces modularity and increases risk of unintended side effects.
- **Fix Example**:
  ```python
  # Instead of global DATA
  def process_data(data):
      return statistics.mean(data)
  ```
- **Best Practice**: Pass data explicitly as parameters or encapsulate logic in classes.

---

### 2. **Duplicate Code**
- **Issue**: Repeated calls to `statistics.mean(DATA)` and `statistics.median(DATA)`.
- **Explanation**: Calculations happen more than once unnecessarily.
- **Why It Happens**: Lack of caching or extraction into helper functions.
- **Impact**: Slower execution and higher chance of inconsistency.
- **Fix Example**:
  ```python
  mean_val = statistics.mean(DATA)
  median_val = statistics.median(DATA)
  ```
- **Best Practice**: Cache results when computations are expensive or reused.

---

### 3. **Implicit Logic**
- **Issue**: Assumptions about array sizes aren’t validated or documented.
- **Explanation**: Code assumes certain lengths or structures without checking.
- **Why It Happens**: No defensive programming or input validation.
- **Impact**: Can cause runtime errors or unexpected behavior on bad inputs.
- **Fix Example**:
  ```python
  assert len(DATA) >= 37, "Not enough data"
  ```
- **Best Practice**: Validate inputs early and fail fast.

---

### 4. **Magic Numbers**
- **Issue**: Hardcoded number `37` lacks clarity or documentation.
- **Explanation**: Readers cannot tell why this value is important.
- **Why It Happens**: Quick fixes without semantic meaning.
- **Impact**: Difficult to change or justify later.
- **Fix Example**:
  ```python
  DEFAULT_LIMIT = 37
  LIMIT = DEFAULT_LIMIT
  ```
- **Best Practice**: Replace magic numbers with named constants.

---

### 5. **Unchecked Input**
- **Issue**: User input from routes isn't sanitized or checked.
- **Explanation**: Vulnerable to invalid or malicious payloads.
- **Why It Happens**: Ignoring validation layers.
- **Impact**: Security flaws and system instability.
- **Fix Example**:
  ```python
  if not isinstance(user_input, list):
      raise ValueError("Invalid input")
  ```
- **Best Practice**: Always validate and sanitize inputs before use.

---

### 6. **Hardcoded Port**
- **Issue**: Server starts on hardcoded port `5000`.
- **Explanation**: Limits deployment flexibility.
- **Why It Happens**: Configuration ignored in favor of simplicity.
- **Impact**: Deployment becomes inflexible and error-prone.
- **Fix Example**:
  ```python
  PORT = int(os.getenv('PORT', 5000))
  app.run(host='0.0.0.0', port=PORT)
  ```
- **Best Practice**: Externalize configuration via environment variables.

---

### 7. **Inconsistent Naming**
- **Issue**: Variable names like `meanAgain`, `medianPlus42` confuse intent.
- **Explanation**: Misleading names hide logic or duplication.
- **Why It Happens**: Rushed naming or lack of style guide enforcement.
- **Impact**: Decreases readability and collaboration.
- **Fix Example**:
  ```python
  mean_value = ...
  median_value = ...
  ```
- **Best Practice**: Choose descriptive and consistent names.

---

### 8. **Single Responsibility Principle Violated**
- **Issue**: Business logic mixed with HTTP response formatting.
- **Explanation**: Routes become bloated and hard to reuse or test.
- **Why It Happens**: No clear separation between concerns.
- **Impact**: Difficult to evolve or refactor cleanly.
- **Fix Example**:
  ```python
  def calculate_stats(data):
      return {"mean": statistics.mean(data), "median": statistics.median(data)}

  @app.route('/analyze')
  def analyze():
      result = calculate_stats(DATA)
      return jsonify(result)
  ```
- **Best Practice**: Separate domain logic from presentation layer.

---

### 9. **Poor Error Handling**
- **Issue**: No checks for edge cases like empty lists or wrong types.
- **Explanation**: Crashes or unpredictable outputs on invalid input.
- **Why It Happens**: Lack of defensive programming.
- **Impact**: System unreliability and debugging difficulties.
- **Fix Example**:
  ```python
  if not DATA:
      return jsonify({"error": "No data"}), 400
  ```
- **Best Practice**: Handle all possible failure modes gracefully.

---

### 10. **Missing Documentation**
- **Issue**: No docstrings or inline comments.
- **Explanation**: Harder for new team members to understand intent.
- **Why It Happens**: Oversight in development workflow.
- **Impact**: Slower onboarding and increased bugs.
- **Fix Example**:
  ```python
  def get_statistics(data):
      """Calculate mean and median of given numeric list."""
      return ...
  ```
- **Best Practice**: Document interfaces and core behaviors clearly.

---

### 11. **Lack of Tests**
- **Issue**: No unit or integration tests exist.
- **Explanation**: Changes may break functionality silently.
- **Why It Happens**: Testing not part of CI/CD pipeline or culture.
- **Impact**: Regression risk grows over time.
- **Fix Example**:
  ```python
  def test_calculate_stats():
      assert calculate_stats([1, 2, 3]) == {'mean': 2.0, 'median': 2}
  ```
- **Best Practice**: Write tests for every major function and flow.