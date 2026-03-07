### 1. **Global Variable Usage**
- **Issue**: Functions access global variables directly instead of receiving them as parameters.
- **Explanation**: This breaks encapsulation and makes code hard to test or reuse.
- **Why It Happens**: Design favors convenience over modularity.
- **Impact**: Side effects and tight coupling reduce maintainability.
- **Fix Example**:
  ```python
  # Before
  def analyzeData():
      return mean(dataFrameLike)

  # After
  def analyzeData(data):
      return mean(data)
  ```
- **Best Practice**: Pass dependencies explicitly.

---

### 2. **Magic Number**
- **Issue**: Hardcoded numeric values without context.
- **Explanation**: Makes future changes risky and unclear.
- **Why It Happens**: Lack of abstraction for configuration.
- **Impact**: Reduced readability and scalability.
- **Fix Example**:
  ```python
  # Before
  if value > 5:

  # After
  MIN_THRESHOLD = 5
  if value > MIN_THRESHOLD:
  ```
- **Best Practice**: Replace magic numbers with named constants.

---

### 3. **Duplicate Computation**
- **Issue**: Same calculations repeated unnecessarily.
- **Explanation**: Wastes CPU cycles and introduces redundancy.
- **Why It Happens**: No caching or reuse of intermediate results.
- **Impact**: Performance degradation and code duplication.
- **Fix Example**:
  ```python
  # Before
  mean_val = statistics.mean(nums)
  median_val = statistics.median(vals)
  mean_val = statistics.mean(nums)  # Duplicate!

  # After
  mean_val = statistics.mean(nums)
  median_val = statistics.median(vals)
  ```
- **Best Practice**: Compute once and store.

---

### 4. **Inconsistent Naming**
- **Issue**: Mix of snake_case and camelCase in variable names.
- **Explanation**: Confuses readers and lowers consistency.
- **Why It Happens**: No style guide enforced during development.
- **Impact**: Lower readability across team.
- **Fix Example**:
  ```python
  # Before
  dataFrameLike = ...
  textOutput = ...

  # After
  data_frame_like = ...
  text_output = ...
  ```
- **Best Practice**: Follow a consistent naming convention.

---

### 5. **Function Side Effects**
- **Issue**: Functions modify global state unexpectedly.
- **Explanation**: Unpredictable behavior due to hidden interactions.
- **Why It Happens**: Mutable shared state is used freely.
- **Impact**: Difficult debugging and unit testing.
- **Fix Example**:
  ```python
  # Before
  def updateStatus(msg):
      statusText.setText(msg)

  # After
  def updateStatus(msg, output_widget):
      output_widget.setText(msg)
  ```
- **Best Practice**: Avoid mutating external state.

---

### 6. **Lack of Documentation**
- **Issue**: Missing docstrings for functions.
- **Explanation**: Harder for others to understand purpose and usage.
- **Why It Happens**: Not prioritized during development.
- **Impact**: Slower onboarding and maintenance.
- **Fix Example**:
  ```python
  def analyzeData(data):
      """Compute mean and median of dataset."""
      return mean(data), median(data)
  ```
- **Best Practice**: Write clear docstrings.

---

### 7. **No Input Validation**
- **Issue**: Assumption that inputs are always valid.
- **Explanation**: Leads to crashes or incorrect outputs.
- **Why It Happens**: No defensive programming practices.
- **Impact**: Unstable behavior under edge cases.
- **Fix Example**:
  ```python
  def process_data(data):
      assert isinstance(data, list), "Input must be a list"
      ...
  ```
- **Best Practice**: Validate input early and fail fast.

---