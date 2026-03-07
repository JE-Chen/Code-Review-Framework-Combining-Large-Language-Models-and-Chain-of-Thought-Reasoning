### Code Review Summary

#### 1. **Readability & Consistency**
- ✅ Indentation and formatting are consistent.
- ⚠️ Comments are missing; consider adding brief inline comments for complex logic (e.g., `time.sleep(0.1)` behavior).

#### 2. **Naming Conventions**
- ❌ `GLOBAL_THING` is too generic and unclear. Should be renamed to something like `app_state` or `window_data`.
- ⚠️ Function names (`compute_title`, `generate_text`) are descriptive but could benefit from more context-specific names (e.g., `update_window_title`, `get_display_text`).

#### 3. **Software Engineering Standards**
- ❌ Global state (`GLOBAL_THING`) makes the code hard to test and maintain. Refactor into instance attributes or a dedicated state manager.
- ⚠️ Duplicate logic: The `handle_click` and `do_periodic_stuff` functions both modify `self.label` and `self.setWindowTitle`. Consider extracting shared behaviors into helper methods.

#### 4. **Logic & Correctness**
- ⚠️ Using `time.sleep(0.1)` in UI thread will block the interface — can cause freezing or unresponsiveness.
- ❌ Hardcoded magic numbers (e.g., `777`, `0.1`, `0.3`, `5`, `7`) should be extracted as constants for clarity and maintainability.

#### 5. **Performance & Security**
- ⚠️ Blocking the UI thread with `time.sleep()` is a major performance concern and may lead to poor UX.
- ⚠️ No input validation or sanitization needed here, but using global mutable state introduces risk of unexpected side effects.

#### 6. **Documentation & Testing**
- ❌ No docstrings or inline comments explaining what each part does.
- ⚠️ Lack of unit tests for core logic (e.g., `generate_text`, `compute_title`). Unit tests would improve confidence in correctness.

#### 7. **Suggestions for Improvement**
- Replace `GLOBAL_THING` with an instance variable or a proper state object.
- Extract hardcoded values into constants at module level.
- Move `time.sleep()` off the main thread using threading or async patterns.
- Add docstrings and inline comments for clarity.
- Abstract repeated UI update logic into helper methods.

---

**Overall Score:** ⚠️ Moderate  
**Next Steps:** Refactor global state, remove blocking calls, and add documentation/comments before moving to advanced features.