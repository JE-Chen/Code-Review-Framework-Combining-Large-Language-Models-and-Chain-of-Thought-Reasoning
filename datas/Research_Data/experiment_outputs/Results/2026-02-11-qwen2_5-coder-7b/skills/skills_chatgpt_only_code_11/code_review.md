### Diff #1
#### Summary
This PR introduces a new module that manages user records, their relationships, and various operations related to these users. The core functionalities include adding users, managing friendships, analyzing user data, and performing cleanup operations.

#### Linting Issues
- **PEP 8 Compliance**: 
  - Line length exceeds 79 characters in several places (e.g., `add_friend_relation`, `get_friends`).
  - Missing spaces around operators (e.g., `pos=None` should be `pos is None`).

#### Code Smells
- **Long Functions**: 
  - `analyze_users()` has a high cyclomatic complexity due to its numerous conditional checks and operations.
  - `find_users_by_age()` could benefit from early returns for better readability.
- **Global State Management**: 
  - Use of global lists (`USERS`, `USER_INDEX`, `MIXED_LOG`) can lead to unexpected side effects and make the code harder to test and debug.
  - Consider encapsulating state within a class to improve modularity.
- **Redundant Operations**: 
  - `duplicate_users()` uses `copy.deepcopy()`, which is unnecessary since `USERS` contains no mutable objects directly. If `USERS` were modified later, this would be important.

### Diff #2
#### Summary
This PR includes additional functionality to handle user inactivity and a simplified version of the `analyze_users()` function.

#### Linting Issues
- **PEP 8 Compliance**: 
  - Similar to the first diff, some lines exceed the recommended line length.
  - Lack of spaces around assignment operators (e.g., `limit=15`).

#### Code Smells
- **Poor Naming**: 
  - Variable names like `FRIEND_A` and `FRIEND_B` are cryptic and do not clearly indicate their purpose.
  - Consider renaming them to something more descriptive, such as `friend_ids_a` and `friend_ids_b`.
- **Magic Numbers**: 
  - The number `15` appears without context in `remove_young_users`. Define it as a constant for clarity.
- **Complexity Increase**: 
  - The introduction of `mark_inactive()` adds another operation but does not significantly improve the overall structure or readability of the code.