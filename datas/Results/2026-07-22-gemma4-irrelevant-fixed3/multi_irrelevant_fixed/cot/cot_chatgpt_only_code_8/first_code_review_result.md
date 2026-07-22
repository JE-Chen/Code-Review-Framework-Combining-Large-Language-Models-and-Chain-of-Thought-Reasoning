### Code Review

**Naming Conventions**
* **Inconsistent Naming:** Variable names follow multiple different conventions (camelCase, snake_case, and abbreviated prefixes). 
    * *Examples:* `nameInput` vs `btn_add_user` vs `txtAge` vs `buttonDelete`.
    * *Suggestion:* Standardize all widget names to a single convention (e.g., `self.name_input`, `self.age_input`, `self.add_button`).

**Logic & Correctness**
* **UI Blocking:** The use of `time.sleep()` in `add_user` and `delete_user` freezes the main GUI thread, making the application unresponsive during those intervals.
    * *Suggestion:* Remove `time.sleep()` or use `QTimer.singleShot` if a delay is intentionally required.
* **Bare Except Clause:** The `try...except:` block in `add_user` catches all exceptions, which can hide unexpected errors.
    * *Suggestion:* Use `except ValueError:` to specifically handle integer conversion failures.

**Software Engineering Standards**
* **Redundant Lambdas:** `clicked.connect(lambda: self.add_user())` is unnecessary.
    * *Suggestion:* Pass the method reference directly: `clicked.connect(self.add_user)`.

**Readability & Consistency**
* **Magic Strings:** Status colors and action types ("add", "delete") are hardcoded as strings.
    * *Suggestion:* Use constants or an Enum for action types to prevent typos and improve maintainability.