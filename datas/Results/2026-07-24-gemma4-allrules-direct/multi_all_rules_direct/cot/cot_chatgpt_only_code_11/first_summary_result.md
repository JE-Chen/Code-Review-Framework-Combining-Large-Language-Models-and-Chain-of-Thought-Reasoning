# Pull Request Summary

## Summary
- **Key changes**: Implemented a basic user management system including user creation, friendship tracking, age-based filtering, and reporting.
- **Impact scope**: Core user data structures and utility functions for user indexing and analysis.
- **Purpose of changes**: Initial implementation of user record handling and relationship mapping.
- **Risks and considerations**: The current implementation relies heavily on global mutable state and positional indexing, which may lead to data inconsistency and scaling issues.
- **Items to confirm**: Review the data integrity of `USER_INDEX` after `remove_young_users` is called.

---

# Code Review

## 1. Readability & Consistency
- **Positional Indexing**: The code uses tuples for user records (e.g., `u[0]`, `u[2]`, `u[3]`). This is highly error-prone and reduces readability. 
  - *Recommendation*: Use a `NamedTuple` or a `dataclass` to provide semantic names (e.g., `user.uid` instead of `u[0]`).

## 2. Naming Conventions
- **Generic Names**: Variables like `s`, `m`, `u`, and `temp` are too short and non-descriptive.
  - *Recommendation*: Rename `s` to `unique_ages`, `m` to `user_map`, and `u` to `user`.

## 3. Software Engineering Standards
- **Modularization**: The code mixes data storage (global lists) with business logic.
  - *Recommendation*: Encapsulate the user management logic within a `UserManager` class to avoid global state.
- **Redundancy**: `build_age_map` creates a dictionary only to immediately convert it into a list of dictionaries. This is an unnecessary intermediate step.

## 4. Logic & Correctness
- **Critical Bug (Index Drift)**: In `remove_young_users`, the code pops elements from `USERS` and `USER_INDEX`. However, `USER_INDEX` stores the *original* positions of users. Once an element is popped from `USERS`, all subsequent indices in `USER_INDEX` become invalid, leading to `find_user_position` returning the wrong user or causing an `IndexError`.
- **Inconsistent State**: `add_friend` updates a user record and a dictionary, while `add_friend_relation` updates two separate global lists (`FRIEND_A`, `FRIEND_B`). This creates two competing sources of truth for friendships.
- **Data Integrity**: `mark_inactive` replaces a tuple in the `USERS` list. Since tuples are immutable, this is handled correctly, but the use of `-1` as a sentinel value for age is a "magic number" and should be a named constant.

## 5. Performance & Security
- **Time Complexity**: `find_user_position` and `get_friends` perform linear searches $O(N)$. 
  - *Recommendation*: Use a dictionary for `USER_INDEX` to achieve $O(1)$ lookups.
- **Memory**: `duplicate_users` uses `copy.deepcopy(USERS)`. For large datasets, this is expensive.

## 6. Documentation & Testing
- **Missing Documentation**: There are no docstrings explaining the expected types of arguments or the purpose of the functions.
- **Testing**: The `main()` function provides a basic smoke test, but there are no formal unit tests to verify edge cases (e.g., adding a friend to a non-existent user).

## 7. RAG Rules Violations
- **Shared Mutable State**: The use of `USERS`, `USER_INDEX`, `MIXED_LOG`, `FRIEND_A`, and `FRIEND_B` as global lists violates the rule against shared mutable state at the module level.
- **Implicit Truthiness**: `if pos is None:` is used correctly, but the logic in `find_users_by_age` relies on `if as_map:`, which is acceptable but could be more explicit.
- **Magic Numbers**: The value `-1` in `mark_inactive` is a magic number.
- **Single Responsibility**: `find_users_by_age` handles both filtering and transformation (converting to a map), violating the single responsibility principle.
- **Returning Different Types**: `find_users_by_age` returns either a `list` or a `dict` based on a flag, which increases the burden on the caller.