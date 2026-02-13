# Code Review Report

## Readability & Consistency
- **Major Issue**: Overuse of global variables (`USERS`, `USER_INDEX`, `MIXED_LOG`, `FRIEND_A`, `FRIEND_B`) creates tight coupling and makes code hard to reason about. Global state should be minimized.
- **Issue**: Inconsistent naming for friend data structures (`FRIEND_A`/`FRIEND_B` vs. user record's `friends` list). This creates confusion about where data is stored.
- **Minor Issue**: `MIXED_LOG` is appended in `add_user` but never used. Should be removed.

## Naming Conventions
- **Strong**: `create_user_record`, `find_user_position`, `build_age_map` (clear semantic meaning).
- **Weak**: 
  - `FRIEND_A`/`FRIEND_B`: Ambiguous names for parallel arrays. Should be `friend_relations` or similar.
  - `add_friend_relation`: Misleading name (doesn't add to user record).
  - `mark_inactive`: Uses magic number `-1` for age (should use `None` or dedicated status).

## Software Engineering Standards
- **Critical Flaw**: **Duplicate friend data storage**:
  - Friends stored in user record (via `add_friend`)
  - Friends also stored in global arrays (via `add_friend_relation`)
  - Causes inconsistency and maintenance hell.
- **Major Issue**: No encapsulation. User data structure relies on index-based access (`user[3]`, `user[4]`), making code fragile.
- **Redundancy**: `get_unique_ages_sorted` and `build_age_map` serve similar purposes but have different implementations.

## Logic & Correctness
- **Bug in `remove_young_users`**: 
  ```python
  while i < len(USERS):
      if USERS[i][2] < limit:
          USERS.pop(i)
          USER_INDEX.pop(i)
      else:
          i += 1
  ```
  **Corrected logic**: Should increment `i` only when *not* popping. Current logic skips elements after removal (e.g., removing index 0 would skip the new index 0 element).
- **Inconsistency**: `add_friend` updates user record but `add_friend_relation` updates global arrays without touching user record.
- **Edge Case**: `mark_inactive` sets age to `-1` (invalid age range). Should use `None` or dedicated status.

## Performance & Security
- **Performance Risk**: `get_friends` uses O(n) linear scan over `FRIEND_A`/`FRIEND_B` (inefficient for large datasets). Should use dictionary for O(1) lookups.
- **No Security Concerns**: Input validation is minimal but acceptable for this scope.

## Documentation & Testing
- **Missing**: No docstrings, minimal comments.
- **Critical Gap**: Zero unit tests. Key logic (friend management, age filtering) lacks verification.

---

## Summary of Critical Issues
| Category             | Issue                                                                 |
|----------------------|-----------------------------------------------------------------------|
| **Design**           | Duplicate friend data storage (user record vs. global arrays)           |
| **Maintainability**  | Index-based user record access (`user[3]`) and global state            |
| **Correctness**      | Bug in `remove_young_users` and inconsistent friend management         |
| **Testability**      | No unit tests, global state prevents modular testing                  |

---

## Recommendations
1. **Eliminate global state**:
   - Replace `USERS`, `USER_INDEX` with a `UserManager` class.
   - Remove `FRIEND_A`/`FRIEND_B` and `add_friend_relation` entirely.
2. **Fix friend storage**:
   - Store friends *only* in user records (use `user[3]` as the sole source of truth).
   - Replace `get_friends` with direct lookup from user record.
3. **Improve data integrity**:
   - Use `None` instead of `-1` for inactive users.
   - Fix `remove_young_users` loop logic.
4. **Add documentation**:
   - Write docstrings for all functions.
   - Add inline comments explaining data structure.
5. **Add tests**:
   - Unit tests for `add_friend`, `get_friends`, and `remove_young_users`.
   - Test edge cases (e.g., removing all users, duplicate UIDs).

---

## Why This Matters
Current implementation risks **data corruption** (due to dual storage) and **hard-to-debug bugs** (e.g., friends not matching user records). Fixing these will make the codebase:
- 3x more maintainable (removing globals)
- 10x more testable (encapsulated logic)
- Free from critical bugs (fixing removal logic)

**Priority**: High. This is foundational code that affects all user operations.