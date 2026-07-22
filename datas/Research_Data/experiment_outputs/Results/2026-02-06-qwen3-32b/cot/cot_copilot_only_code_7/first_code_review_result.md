- **Global State Abuse**: Replace all global variables (`GLOBAL_TEXT`, `GLOBAL_COUNTER`, `GLOBAL_MODE`) with instance attributes. Globals break encapsulation, make testing impossible, and create hidden dependencies. Example: Store text counter in `self.counter` instead of `GLOBAL_COUNTER`.
  
- **Inconsistent Naming**: Event handlers like `handle_btn1` are unclear. Rename to descriptive names like `on_add_text` or `handle_text_input` for better readability and intent.

- **Status Label Ambiguity**: The label "Status: Updated" is vague. Change to "Status: Text added" or similar for immediate user feedback clarity.

- **Missing Documentation**: Add class-level docstring and method summaries explaining purpose, e.g., `"""Handles text addition. Updates global text buffer and counter."""`.

- **Redundant Global Prefix**: The `GLOBAL_` prefix is unnecessary noise. If globals were unavoidable (which they aren’t), use meaningful names without prefixes.

- **Mode Logic Complexity**: The `handle_btn2` condition is nested and unclear. Simplify with early returns or extract helper methods to avoid deep nesting.

- **No State Reset Clarity**: `GLOBAL_MODE = "reset"` in `handle_btn3` lacks context. Clarify purpose via comment or rename to `self.mode = "reset"` (after fixing global state).