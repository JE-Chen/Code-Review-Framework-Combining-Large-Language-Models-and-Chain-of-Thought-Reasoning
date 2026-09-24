### Code Review

**Naming Conventions**
* **Inconsistent Naming:** Variable names follow multiple styles (camelCase, snake_case, and abbreviated prefixes). 
    * *Examples:* `nameInput` vs `btn_add_user` vs `txtAge` vs `buttonDelete`.
    * *Suggestion:* Use consistent `snake_case` for all attributes (e.g., `name_input`, `age_input`, `delete_button`).

**Logic & Correctness**
* **UI Blocking:** `time.sleep()` is called on the main GUI thread in `add_user` and `delete_user`. This freezes the application interface and prevents it from responding to events.
    * *Suggestion:* Remove `time.sleep()` or use a non-blocking approach if a delay is required.
* **Bare Except Clause:** The `try...except` block in `add_user` catches all exceptions.
    * *Suggestion:* Change to `except ValueError:` to specifically handle integer conversion errors.

**Software Engineering Standards**
* **Redundant Lambdas:** `lambda: self.add_user()` and `lambda: self.delete_user()` are unnecessary as the methods take no arguments.
    * *Suggestion:* Connect directly: `self.btn_add_user.clicked.connect(self.add_user)`.

**Performance & Security**
* **Inefficient Styling:** `refresh_status` is called every second via `QTimer` and updates the stylesheet regardless of whether the color has actually changed.
    * *Suggestion:* Update the style only when `last_action` changes, or check if the current style matches the target style before applying.