### Code Review

**Naming Conventions**
* **Inconsistent Naming:** Variable names follow multiple different conventions (camelCase, snake_case, and abbreviated prefixes).
    * *Examples:* `nameInput` (camelCase), `btn_add_user` (snake_case), `txtAge` (prefix + camelCase), `buttonDelete` (camelCase).
    * *Suggestion:* Standardize all member variables to `snake_case` (e.g., `name_input`, `age_input`, `delete_button`) to follow PEP 8.

**Logic & Correctness**
* **UI Blocking:** The use of `time.sleep()` inside `add_user` and `delete_user` freezes the main GUI thread, making the application unresponsive during those intervals.
    * *Suggestion:* Remove `time.sleep()` or use a non-blocking approach if a delay is required.
* **Bare Except Clause:** The `try...except:` block in `add_user` catches all exceptions, which can hide unexpected errors.
    * *Suggestion:* Use `except ValueError:` to specifically handle integer conversion failures.

**Software Engineering Standards**
* **Redundant Lambdas:** `clicked.connect(lambda: self.add_user())` is unnecessary.
    * *Suggestion:* Pass the method reference directly: `clicked.connect(self.add_user)`.

**Performance & Security**
* **Inefficient Style Updates:** `refresh_status` is called every second by a `QTimer` and updates the stylesheet regardless of whether the state has changed.
    * *Suggestion:* Update the style only when `last_action` changes, or check if the current style already matches the target state before applying it.