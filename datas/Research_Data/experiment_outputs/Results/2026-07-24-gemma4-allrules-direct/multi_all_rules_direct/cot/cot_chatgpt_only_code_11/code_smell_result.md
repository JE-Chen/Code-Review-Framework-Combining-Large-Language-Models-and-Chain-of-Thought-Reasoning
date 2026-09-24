- Code Smell Type: Shared Mutable State (Global Variables)
- Problem Location: `USERS = []`, `USER_INDEX = []`, `MIXED_LOG = []`, `FRIEND_A = []`, `FRIEND_B = []`
- Detailed Explanation: The application relies heavily on global lists to store state. This creates hidden coupling between functions, making the code difficult to test in isolation and impossible to use in a multi-threaded environment or a scenario where multiple independent user sets are needed. It violates the principle of encapsulating state within well-defined objects.
- Improvement Suggestions: Encapsulate the user management logic into a `UserManager` class. Pass the state as an instance attribute rather than relying on module-level globals.
- Priority Level: High

- Code Smell Type: Use of Magic Indexes (Lack of Data Structuring)
- Problem Location: `user[0]`, `user[2]`, `user[3]`, `user[4]` (throughout `add_friend`, `build_age_map`, `find_users_by_age`, etc.)
- Detailed Explanation: Users are represented as tuples. Accessing data via numeric indices (e.g., `u[2]` for age) is error-prone and reduces readability. If the tuple structure changes (e.g., adding a field), every single index reference across the codebase must be manually updated, which is highly fragile.
- Improvement Suggestions: Use a `dataclass` or a `NamedTuple` to represent a User. This allows accessing attributes by name (e.g., `user.age`) instead of index.
- Priority Level: High

- Code Smell Type: Inconsistent Return Types
- Problem Location: `find_users_by_age(min_age, as_map=False)`
- Detailed Explanation: The function returns a `list` if `as_map` is False and a `dict` if `as_map` is True. This forces the caller to know the internal state of the flag to handle the return value correctly, increasing the risk of `TypeError` or `AttributeError` at runtime.
- Improvement Suggestions: Split this into two distinct functions: `find_users_by_age_list()` and `find_users_by_age_map()`.
- Priority Level: Medium

- Code Smell Type: Violation of Single Responsibility Principle (SRP)
- Problem Location: `remove_young_users(limit)`
- Detailed Explanation: This function is responsible for both the business logic of identifying "young" users and the low-level synchronization of two separate data structures (`USERS` and `USER_INDEX`). If a third index is added later, this function becomes a bottleneck and a source of bugs.
- Improvement Suggestions: Implement a centralized `delete_user(index)` method that handles the cleanup of all associated indices, and have `remove_young_users` call that method.
- Priority Level: Medium

- Code Smell Type: Inefficient Data Structures / Algorithmic Complexity
- Problem Location: `find_user_position(uid)` and `get_friends(uid)`
- Detailed Explanation: `find_user_position` performs a linear search $O(N)$ through a list of pairs. Similarly, `get_friends` iterates through the entire `FRIEND_A` list $O(N)$. As the dataset grows, these operations will significantly degrade performance.
- Improvement Suggestions: Use a dictionary for `USER_INDEX` to allow $O(1)$ lookups by `uid`. Use an adjacency list (dictionary of lists) for friend relations.
- Priority Level: Medium