### Code Review Summary

#### 1. **Readability & Consistency**
- Inconsistent use of naming styles (e.g., `FRIEND_A`, `FRIEND_B` vs `USERS`, `USER_INDEX`).
- Comments are missing; some functions lack inline documentation.
- Formatting is generally acceptable but could benefit from consistent spacing and alignment.

#### 2. **Naming Conventions**
- Variables like `FRIEND_A`, `FRIEND_B` are non-descriptive and hard to understand without context.
- Function names such as `add_friend_relation` do not clearly express their role in the system.
- Global variables (`USERS`, `USER_INDEX`) make it harder to reason about data flow and state changes.

#### 3. **Software Engineering Standards**
- Heavy reliance on global mutable state leads to tight coupling and poor modularity.
- Duplicated logic exists in `build_age_map()` and `find_users_by_age()` — can be abstracted.
- No encapsulation or clear interfaces for managing users or relationships.

#### 4. **Logic & Correctness**
- Potential race condition or inconsistency when updating shared mutable structures (`USERS`, `USER_INDEX`) during concurrent operations.
- Incorrect behavior in `remove_young_users`: removal of items modifies indices mid-loop, causing skipped elements.
- `mark_inactive` changes a user's age to `-1` without clear semantic meaning or validation.

#### 5. **Performance & Security**
- Linear search through lists (`find_user_position`, `get_friends`) results in O(n) complexity which scales poorly.
- No input validation for `uid`, `friend_id`, etc., making the system vulnerable to invalid data.

#### 6. **Documentation & Testing**
- Missing docstrings or inline comments explaining intent or usage.
- No unit tests provided for core functionality.

#### 7. **Suggestions for Improvement**
- Refactor into classes/modules to encapsulate state and reduce global dependencies.
- Replace list-based lookups with hash maps for faster access.
- Use proper error handling instead of silent failures.
- Improve naming to increase clarity and maintainability.
- Add input validation and assertions where needed.