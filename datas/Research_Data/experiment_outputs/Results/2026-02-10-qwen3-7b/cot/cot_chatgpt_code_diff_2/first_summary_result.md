### PR Summary Template

- **Summary**: Implement core game loop and state updates; improve readability and maintainability.
- **Impact**: Affected `game.py`; core game mechanics and rendering logic.
- **Purpose**: Simplify state management, enhance clarity, and ensure robustness.
- **Risks**: Potential score calculation bugs; unclear movement logic.
- **Items to Confirm**: Correct score logic, consistent naming, and comments.
- **High-Level Points**: Simplify state updates, modularize functions, and add documentation.

---

### Code Review

---

#### 1. **Readability & Consistency**
- **Issue**: Indentation inconsistency and unclear variable names.
- **Fix**: Standardize indentation (4 spaces), rename `STATE` to `game_state` and `player` to `player_pos`.

---

#### 2. **Naming Conventions**
- **Issue**: `STATE` and `color` are ambiguous; `velocity` is underused.
- **Fix**: Use `game_state`, `player_pos`, and `color` as explicit variables.

---

#### 3. **Software Engineering Standards**
- **Issue**: Functions are too small; duplicated logic (e.g., key handling).
- **Fix**: Modularize `do_everything` and `move_player` into separate functions.

---

#### 4. **Logic & Correctness**
- **Issue**: Score calculation in `do_everything` is incorrect.
- **Fix**: Use `delta * 10` to accumulate score over time.
- **Issue**: Player movement logic is flawed.
- **Fix**: Simplify velocity handling and ensure bounds.

---

#### 5. **Performance & Security**
- **Issue**: No input validation for color changes.
- **Fix**: Add bounds checking for color values.

---

#### 6. **Documentation & Testing**
- **Issue**: No comments or tests.
- **Fix**: Add docstrings and include unit tests for critical functions.

---

### Key Improvements
- Simplify game state updates.
- Modularize core logic.
- Add clear documentation and validation.