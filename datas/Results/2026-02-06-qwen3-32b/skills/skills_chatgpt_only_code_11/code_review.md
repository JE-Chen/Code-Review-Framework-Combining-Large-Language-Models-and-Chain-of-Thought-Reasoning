### Diff #1

#### **Summary**
This diff introduces a procedural user management system with global state for tracking users, friendships, and age data. It adds functions to create users, manage friendships (via two inconsistent mechanisms), index users, filter by age, and generate reports. The core functionality demonstrates a simple social network simulation in the `main()` function. Key files affected: `user_management.py` (implied file name). Non-experts: This code models users with attributes like name, age, and friends, enabling operations like adding friends and filtering users by age.

---

#### **Linting Issues**
- **Global variable naming inconsistency**:  
  `USERS`, `USER_INDEX`, `MIXED_LOG`, `FRIEND_A`, and `FRIEND_B` are all mutable globals but named like constants (uppercase). This confuses intent.  
  *Suggestion*: Rename to `users`, `user_index`, `mixed_log`, `friend_a`, `friend_b` (lowercase) or encapsulate in a class.

- **Magic numbers in `main()`**:  
  `random.randint(10, 40)` and `remove_young_users(15)` use unexplained values.  
  *Suggestion*: Define constants like `MIN_AGE = 10`, `MAX_AGE = 40`, `MIN_ACTIVE_AGE = 15`.

- **Inefficient string concatenation**:  
  `"User" + str(i)` in `add_user()`.  
  *Suggestion*: Use f-strings: `f"User{i}"`.

- **Missing type hints**:  
  All functions lack type annotations (e.g., `def add_user(uid: int, name: str, age: int) -> None`).  
  *Suggestion*: Add type hints for clarity and tooling support.

---

#### **Code Smells**
- **Global state dependency**:  
  *Problem*: Heavy reliance on global lists (`USERS`, `USER_INDEX`, etc.) breaks encapsulation. Functions like `add_friend()` mutate global state directly.  
  *Impact*: Hard to test, reuse, or scale. Example: `add_friend()` depends on `FRIEND_A`/`FRIEND_B` (from `add_friend_relation`), creating hidden coupling.  
  *Fix*: Encapsulate state in a `UserManager` class with methods like `add_user()`, `add_friend()`.

- **Inconsistent friendship representation**:  
  *Problem*: Two mechanisms for friendships:  
  1. `add_friend_relation(a, b)` stores pairs in `FRIEND_A`/`FRIEND_B` (lists of separate IDs).  
  2. `add_friend(uid, friend_id)` appends to user's own `friends` list.  
  *Impact*: Logic errors (e.g., `get_friends()` uses `FRIEND_A`/`FRIEND_B`, but `add_friend()` updates `USERS`).  
  *Fix*: Standardize on one mechanism (e.g., store all friendships in a single `user_friends` dictionary).

- **Poor data structure choices**:  
  *Problem*:  
  - User records as tuples (`(uid, name, age, friends, extra)`). Indexing via `USERS[i][2]` is fragile (magic index `2` for age).  
  - `find_user_position()` scans `USER_INDEX` linearly (O(n)) instead of using a dictionary for O(1) lookups.  
  *Impact*: Hard to maintain and prone to bugs (e.g., if tuple structure changes).  
  *Fix*: Use named tuples or classes for user records. Replace `USER_INDEX` with a `user_id_to_index` dictionary.

- **Inefficient age processing**:  
  *Problem*:  
  - `get_unique_ages_sorted()` builds a set then converts to list.  
  - `find_users_by_age()` iterates `USERS` twice (once for filtering, once for `as_map`).  
  *Impact*: Suboptimal performance.  
  *Fix*: Use list comprehensions and single-pass logic (e.g., `return sorted(set(u[2] for u in USERS))`).

- **Side effects in `mark_inactive()`**:  
  *Problem*: Mutates `USERS` by replacing a tuple (immutable) with a new tuple.  
  *Impact*: Inconsistent state if other code relies on the original user record.  
  *Fix*: Use an `is_active` flag in user metadata instead of overwriting age.

- **Unused abstraction**:  
  *Problem*: `duplicate_users()` uses `copy.deepcopy()` on tuples (which are immutable). A shallow copy suffices.  
  *Impact*: Unnecessary overhead.  
  *Fix*: Replace with `return USERS[:]` (shallow copy of list).