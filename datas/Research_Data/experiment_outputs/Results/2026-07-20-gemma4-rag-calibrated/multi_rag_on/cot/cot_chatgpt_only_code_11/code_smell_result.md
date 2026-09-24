- Code Smell Type: Use of Magic Indexes (Lack of Data Abstraction)
- Problem Location: Throughout the codebase, specifically in `create_user_record`, `add_friend`, `build_age_map`, `find_users_by_age`, and `mark_inactive`.
- Detailed Explanation: The user record is stored as a tuple (e.g., `u[0]`, `u[2]`, `u[3]`). This makes the code extremely fragile and difficult to read. A developer must memorize that index `0` is UID, `2` is age, and `3` is friends. If the tuple structure changes (e.g., adding a "gender" field at index 2), every single function accessing the user record will break or produce silent logic errors.
- Improvement Suggestions: Replace the tuple with a `dataclass` or a `NamedTuple`. This allows accessing fields by name (e.g., `user.age` instead of `user[2]`), improving readability and maintainability.
- Priority Level: High

- Code Smell Type: Tight Coupling & Data Inconsistency (Parallel Arrays)
- Problem Location: `USER_INDEX`, `FRIEND_A`, and `FRIEND_B`.
- Detailed Explanation: The system maintains user data across multiple global lists that must be kept in sync manually. For example, `remove_young_users` must remember to pop from both `USERS` and `USER_INDEX`. If one is updated and the other is forgotten, the system enters an inconsistent state. Furthermore, `FRIEND_A` and `FRIEND_B` act as a manual implementation of a relationship table, which is inefficient and error-prone.
- Improvement Suggestions: Use a dictionary for `USERS` where the key is the `uid`. This eliminates the need for `USER_INDEX` and `find_user_position` entirely. Store friend relationships within the User object or a dedicated `Relationship` class.
- Priority Level: High

- Code Smell Type: Violation of Single Responsibility Principle (SRP)
- Problem Location: `find_users_by_age(min_age, as_map=False)`
- Detailed Explanation: The function is performing two different tasks: filtering users by age and transforming the result into a different data structure (list vs. map). This "flag argument" pattern indicates the function is doing too much, making the return type unpredictable for the caller.
- Improvement Suggestions: Split this into two functions: `find_users_by_age` (returning a list) and `get_user_map_by_age` (which calls the first and converts the result).
- Priority Level: Medium

- Code Smell Type: Inefficient Algorithm / Time Complexity
- Problem Location: `find_user_position(uid)` and `get_friends(uid)`
- Detailed Explanation: Both functions perform linear searches (`O(n)`) through lists. As the number of users or friendships grows, the performance will degrade linearly. `get_friends` iterates through the entire `FRIEND_A` list every time it is called, even if the user has no friends.
- Improvement Suggestions: Use a dictionary for user lookups and a set or list within the User object for friends to achieve `O(1)` or `O(k)` lookup time.
- Priority Level: Medium

- Code Smell Type: Environment-Dependent Logic (Non-Deterministic)
- Problem Location: `main()` calling `random.randint(10, 40)`
- Detailed Explanation: Per the RAG rules, direct calls to random number generators should be isolated. Currently, the `main` function creates users with random ages, making the output of the program non-deterministic and difficult to unit test.
- Improvement Suggestions: Pass a seed to the random generator or abstract the user creation into a factory that can be mocked during testing.
- Priority Level: Low