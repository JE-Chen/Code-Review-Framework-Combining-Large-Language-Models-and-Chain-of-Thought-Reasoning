- Code Smell Type: Use of Magic Indexes (Data Clumps/Primitive Obsession)
- Problem Location: Throughout the codebase, specifically `user[0]`, `user[1]`, `user[2]`, `user[3]`, `user[4]`.
- Detailed Explanation: The user record is stored as a tuple. Accessing data via numeric indices (e.g., `u[2]` for age) is error-prone and makes the code difficult to read. If the tuple structure changes (e.g., adding a field), every single index reference across the entire application must be manually updated, leading to high maintenance costs and potential bugs.
- Improvement Suggestions: Replace the tuple with a `dataclass` or a `NamedTuple`. This allows accessing fields by name (e.g., `user.age`), which is self-documenting and robust.
- Priority Level: High

- Code Smell Type: Inconsistent Data Storage (Parallel Arrays/Split State)
- Problem Location: `USERS`, `USER_INDEX`, `FRIEND_A`, and `FRIEND_B`.
- Detailed Explanation: User data is fragmented across four different global lists. Friendships are tracked in two different ways: once inside the user tuple (`user[3]`) and once in parallel arrays (`FRIEND_A`/`FRIEND_B`). This creates a "source of truth" conflict. For example, `add_friend` updates the user record, but `get_friends` only reads from the parallel arrays, meaning `get_friends` will never return friends added via `add_friend`.
- Improvement Suggestions: Consolidate all user-related data into a single User object. Store friendships as a list of IDs within that object or in a single dedicated mapping (e.g., a dictionary of sets).
- Priority Level: High

- Code Smell Type: Poor Time/Space Complexity (Inefficient Lookups)
- Problem Location: `find_user_position(uid)` and `get_friends(uid)`.
- Detailed Explanation: Both functions perform linear searches ($O(n)$) through lists to find a specific ID. As the number of users or friendships grows, the performance will degrade linearly. `find_user_position` is called frequently, making this a significant bottleneck.
- Improvement Suggestions: Use a dictionary (`dict`) for `USER_INDEX` and friendship mappings to achieve $O(1)$ average-time complexity for lookups.
- Priority Level: Medium

- Code Smell Type: Fragile State Management (Index Out of Sync)
- Problem Location: `remove_young_users(limit)`
- Detailed Explanation: The function pops elements from `USERS` and `USER_INDEX` based on the current loop index. However, `USER_INDEX` stores the *original* position of the user. Once a single user is removed, all subsequent positions stored in `USER_INDEX` become incorrect, rendering `find_user_position` broken for all users shifted by the pop operation.
- Improvement Suggestions: Avoid storing indices as values. Use a dictionary where the key is the `uid` and the value is the user object.
- Priority Level: High

- Code Smell Type: Violation of Single Responsibility Principle (SRP)
- Problem Location: `find_users_by_age(min_age, as_map=False)`
- Detailed Explanation: The function is doing two different things: filtering a list and transforming the output format based on a boolean flag. This makes the function harder to test and reuse.
- Improvement Suggestions: Split this into two functions: one for filtering (`find_users_by_age`) and a separate utility to convert a list to a map if needed.
- Priority Level: Low