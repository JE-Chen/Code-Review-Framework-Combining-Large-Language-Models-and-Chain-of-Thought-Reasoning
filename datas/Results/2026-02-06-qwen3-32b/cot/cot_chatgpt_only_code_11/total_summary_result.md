### Overall conclusion
The PR **fails to meet merge criteria** due to critical design flaws and unaddressed bugs. The core issues are blocking and must be resolved before merging, as they risk data corruption and inconsistent behavior. Non-blocking concerns (e.g., missing docstrings) are secondary to the structural problems.

### Comprehensive evaluation
- **Code quality & correctness**:  
  Critical bugs exist in `remove_young_users` (loop skips elements after deletion) and `mark_inactive` (uses `-1` for age, violating domain semantics). Duplicate friend storage (`FRIEND_A`/`FRIEND_B` vs. user records) creates data inconsistency and is confirmed by both linter and code smell analysis. The `get_friends` function’s O(n) scan is inefficient and redundant given the flawed data model.

- **Maintainability & design**:  
  Global state (`USERS`, `USER_INDEX`, etc.) and parallel arrays (`FRIEND_A`/`FRIEND_B`) violate encapsulation principles. This makes the code brittle (e.g., index out-of-bounds from `USER_INDEX`), untestable, and error-prone. The linter explicitly flags index storage as unsafe, while code smells confirm the design is unmaintainable.

- **Consistency with standards**:  
  The diff violates naming conventions (`FRIEND_A`/`FRIEND_B`), data structure patterns (parallel arrays), and consistency (e.g., `add_friend` updates user records but `add_friend_relation` bypasses them). This contradicts the team’s implicit expectations for data integrity and semantic clarity.

### Final decision recommendation
**Request changes**  
*Justification*:  
1. The duplicate storage of friends (user records vs. global arrays) is a **critical design flaw** causing data inconsistency.  
2. The `remove_young_users` bug **breaks core functionality** (skips elements after deletion), risking silent data loss.  
3. The negative age (`-1`) for inactive users is **non-standard and confusing**, violating domain semantics.  
These issues cannot be mitigated by minor fixes and require a full refactor to eliminate global state and redundant storage.

### Team follow-up
1. **Refactor to eliminate global state**: Replace all global lists with a `UserManager` class (as suggested in linter and code smell results).  
2. **Fix the friend storage model**:  
   - Remove `FRIEND_A`/`FRIEND_B` and `add_friend_relation`.  
   - Store friends exclusively in user records (e.g., `user[3]` as the sole source of truth).  
3. **Address the critical bug**:  
   - Correct `remove_young_users` to increment `i` *only* when not popping.  
   - Replace `-1` with `None` or a dedicated `is_inactive` flag.  
4. **Add missing documentation**:  
   - Docstrings for all functions (per linter).  
   - Clarify data structures (e.g., `user` record format).  
5. **Implement unit tests**:  
   - Test edge cases for `remove_young_users` and friend management.  
   - Verify data consistency after all operations.  

*Note: The linter’s "duplicate-uid" warning and code smell about `build_age_map` being unused are non-blocking but should be addressed in the same refactor.*