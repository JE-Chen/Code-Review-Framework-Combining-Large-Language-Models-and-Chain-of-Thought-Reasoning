- Code Smell Type: Use of Magic Indexes (Data Clumping/Lack of Domain Objects)
- Problem Location: Throughout the codebase, specifically `user[0]`, `user[1]`, `user[2]`, `user[3]`, `user[4]`.
- Detailed Explanation: The user record is stored as a tuple. Accessing data via numeric indices (e.g., `u[2]` for age) is error-prone and makes the code difficult to read and maintain. If the structure of the user record changes (e.g., adding a field in the middle), every single index reference across the entire application must be manually updated, which is highly susceptible to bugs.
- Improvement Suggestions: Replace the tuple with a `dataclass` or a named class. This allows accessing attributes by name (e.g., `user.age` instead of `user[2]`).
- Priority Level: High

- Code Smell Type: Inconsistent Data Storage (Parallel Arrays/Duplicate State)
- Problem Location: `USERS`, `USER_INDEX`, `FRIEND_A`, and `FRIEND_B`.
- Detailed Explanation: The system stores user relationships in two completely different ways: `add_friend` modifies a list inside the `USERS` tuple, while `add_friend_relation` populates two parallel arrays (`FRIEND_A` and `FRIEND_B`). This creates a "split brain" scenario where the source of truth for friendships is fragmented. Furthermore, `USER_INDEX` is a manual attempt to implement a map using a list of pairs, which is inefficient and redundant.
- Improvement Suggestions: 
    1. Use a dictionary for `USERS` where the key is the `uid` for $O(1)$ lookup, eliminating the need for `USER_INDEX`.
    2. Consolidate friendship logic into a single mechanism (preferably a set of IDs within the User object).
- Priority Level: High

- Code Smell Type: Violation of Single Responsibility Principle (SRP) / Poor Interface Design
- Problem Location: `find_users_by_age(min_age, as_map=False)`
- Detailed Explanation: The function is attempting to do two different things: return a list of users or return a map of users. Using a boolean flag to change the return type of a function is a code smell that forces the caller to know the internal implementation details and makes type hinting/static analysis difficult.
- Improvement Suggestions: Split this into two distinct functions: `find_users_by_age()` and `map_users_by_age()`, or have one function return the list and let the caller convert it to a map if needed.
- Priority Level: Medium

- Code Smell Type: Logic Bug / Data Corruption
- Problem Location: `remove_young_users(limit)`
- Detailed Explanation: The function pops elements from `USERS` and `USER_INDEX` by index. However, `USER_INDEX` contains pairs of `[uid, position]`. When an element is popped from `USERS`, the `position` stored in all subsequent entries of `USER_INDEX` becomes incorrect (off-by-one), rendering `find_user_position` broken for all users shifted in the list.
- Improvement Suggestions: Use a dictionary for user storage. Removing a key from a dictionary does not affect the indexing of other elements.
- Priority Level: High

- Code Smell Type: Inefficient Algorithm (Linear Search)
- Problem Location: `find_user_position(uid)` and `get_friends(uid)`
- Detailed Explanation: Both functions iterate through the entire list to find a specific ID. As the number of users or friendships grows, the performance will degrade linearly ($O(n)$).
- Improvement Suggestions: Use a dictionary for user lookups and a dictionary/set for friendship lookups to achieve $O(1)$ average time complexity.
- Priority Level: Medium