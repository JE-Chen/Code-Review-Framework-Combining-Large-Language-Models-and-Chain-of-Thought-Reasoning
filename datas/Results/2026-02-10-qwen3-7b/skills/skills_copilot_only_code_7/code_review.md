### Diff #1
#### Summary
The PR adds a simple GUI application with buttons for adding text, showing a counter, and resetting. The code uses global variables for state management. The main functions handle user interactions and UI updates.

---

#### Linting Issues
- **Line length**: Lines like `self.btn1.clicked.connect(self.handle_btn1)` exceed 79 characters.
- **Missing spaces**: Improper spacing around operators (e.g., `self.btn1.clicked.connect(self.handle_btn1)`).
- **Global variables**: Global variables `GLOBAL_TEXT`, `GLOBAL_COUNTER`, and `GLOBAL_MODE` are used throughout the code.

---

#### Code Smells
- **Global state**: The code relies on global variables for state management, making it hard to test and maintain.
- **Tight coupling**: `handle_btn2` contains complex logic tied to the counter and mode.
- **Poor naming**: `GLOBAL_MODE` is not descriptive and could be renamed to something like `MODE`.