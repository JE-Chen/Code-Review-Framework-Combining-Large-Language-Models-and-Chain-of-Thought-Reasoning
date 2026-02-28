### 1. **Global Variable Usage (`no-global-variables`)**
- **Issue**: The code uses a global variable `GLOBAL_THING` across multiple methods, reducing modularity and testability.
- **Explanation**: Using global variables makes it hard to understand dependencies, leads to side effects, and complicates unit testing.
- **Root Cause**: Instead of encapsulating state within a class, the code relies on shared mutable state.
- **Impact**: Decreases maintainability, testability, and increases risk of bugs due to unexpected interactions.
- **Fix Suggestion**: Move `GLOBAL_THING` contents into instance attributes (e.g., `self._clicks`, `self._mood`, `self._started`) initialized in `__init__`.
  ```python
  class MyWindow(QWidget):
      def __init__(self):
          super().__init__()
          self._clicks = 0
          self._mood = "neutral"
          self._started = False
  ```
- **Best Practice**: Prefer encapsulation over global state to improve code clarity and testability.

---

### 2. **Unused Variable (`no-unused-vars`)**
- **Issue**: A variable `layout` is defined but never used.
- **Explanation**: Unused variables clutter the code and can confuse developers.
- **Root Cause**: Likely leftover from previous implementation or debugging.
- **Impact**: Minor impact on readability, but indicates incomplete refactoring.
- **Fix Suggestion**: Remove the unused variable.
  ```python
  # Remove this line if layout is unused:
  # layout = QVBoxLayout()
  ```
- **Best Practice**: Regularly review and clean up unused variables during code reviews.

---

### 3. **Magic Number – Timer Interval (`no-magic-numbers`)**
- **Issue**: The number `777` is used directly for timer interval.
- **Explanation**: Hardcoded values reduce readability and make future changes harder.
- **Root Cause**: Lack of abstraction for configuration values.
- **Impact**: Makes maintenance difficult if value needs updating later.
- **Fix Suggestion**: Define a named constant.
  ```python
  DEFAULT_TIMER_INTERVAL_MS = 777
  self.timer.start(DEFAULT_TIMER_INTERVAL_MS)
  ```
- **Best Practice**: Use descriptive constants instead of magic numbers.

---

### 4. **Magic Number – Sleep Duration (`no-magic-numbers`)**
- **Issue**: The value `0.1` is used for sleep duration.
- **Explanation**: Similar to above, it reduces clarity and maintainability.
- **Root Cause**: Direct use of raw numeric literals.
- **Impact**: Future modification requires searching all instances.
- **Fix Suggestion**: Replace with a constant.
  ```python
  CLICK_DELAY_SECONDS = 0.1
  time.sleep(CLICK_DELAY_SECONDS)
  ```
- **Best Practice**: Avoid magic numbers by defining meaningful constants.

---

### 5. **Magic Number – Click Threshold (`no-magic-numbers`)**
- **Issue**: The number `5` is used in a modulo check.
- **Explanation**: This makes the purpose unclear without additional context.
- **Root Cause**: Lack of abstraction for threshold logic.
- **Impact**: Reduces understanding of the logic.
- **Fix Suggestion**: Define as a named constant.
  ```python
  SLOW_CLICK_THRESHOLD = 5
  if clicks % SLOW_CLICK_THRESHOLD == 0:
      ...
  ```
- **Best Practice**: Use constants for meaningful thresholds or limits.

---

### 6. **Magic Number – Event Trigger Frequency (`no-magic-numbers`)**
- **Issue**: The number `7` is used in periodic logic.
- **Explanation**: Without explanation, it's unclear what this number represents.
- **Root Cause**: Not abstracted into a named constant.
- **Impact**: Makes the code harder to understand and update.
- **Fix Suggestion**: Replace with a descriptive constant.
  ```python
  EVENT_TRIGGER_INTERVAL = 7
  if counter % EVENT_TRIGGER_INTERVAL == 0:
      ...
  ```
- **Best Practice**: Name your configuration values so their purpose is obvious.

---

### 7. **Magic Number – Probability Value (`no-magic-numbers`)**
- **Issue**: The value `0.3` is used in a probability check.
- **Explanation**: It’s unclear what `0.3` stands for without comments.
- **Root Cause**: Missing abstraction for probabilities or percentages.
- **Impact**: Less readable and maintainable.
- **Fix Suggestion**: Use a named constant.
  ```python
  BUTTON_TEXT_CHANGE_PROBABILITY = 0.3
  if random.random() < BUTTON_TEXT_CHANGE_PROBABILITY:
      ...
  ```
- **Best Practice**: Always name numeric probabilities or percentages for clarity.

---

### 8. **Blocking UI with `time.sleep()` (`no-sync-in-event-loop`)**
- **Issue**: `time.sleep(0.1)` blocks the main thread, freezing the UI.
- **Explanation**: In GUI apps, blocking calls cause poor responsiveness.
- **Root Cause**: Misuse of synchronous delay in event handlers.
- **Impact**: Poor UX and potential app crashes due to unresponsive interface.
- **Fix Suggestion**: Replace with async alternative.
  ```python
  QTimer.singleShot(100, lambda: self.apply_delay())
  ```
- **Best Practice**: Never block the main thread in GUI applications.

---

### 9. **Code Duplication (`no-duplicated-code`)**
- **Issue**: Similar logic exists in `handle_click` and `do_periodic_stuff`.
- **Explanation**: Repetitive code blocks increase chances of inconsistencies and bugs.
- **Root Cause**: Lack of reusable helper functions.
- **Impact**: Makes future changes harder and increases maintenance cost.
- **Fix Suggestion**: Extract duplicated logic into a shared method.
  ```python
  def handle_common_logic(self, condition):
      if condition:
          # shared code here
  ```
- **Best Practice**: Apply DRY (Don’t Repeat Yourself) principle to reduce redundancy.

---

### 10. **Hardcoded Strings (`no-hardcoded-strings`)**
- **Issue**: Strings like `"Click maybe"` and `"Don't click"` appear directly in code.
- **Explanation**: Makes localization and theming difficult.
- **Root Cause**: No central place to manage UI text.
- **Impact**: Limits scalability and internationalization support.
- **Fix Suggestion**: Store strings in a dictionary or constants.
  ```python
  BUTTON_TEXTS = {
      "click_maybe": "Click maybe",
      "dont_click": "Don't click"
  }
  button.setText(BUTTON_TEXTS["click_maybe"])
  ```
- **Best Practice**: Externalize UI strings for easier translation and customization.

---