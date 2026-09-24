```json
[
  {
    "rule_id": "software-engineering-standards",
    "severity": "error",
    "message": "The code uses tuples to represent user records (e.g., user[0], user[2]), which is fragile and reduces readability. This makes the code hard to maintain if the record structure changes.",
    "line": 7,
    "suggestion": "Use a namedtuple, a dataclass, or a class to define the User record with named attributes."
  },
  {
    "rule_id": "logic-correctness",
    "severity": "error",
    "message": "The remove_young_users function pops elements from USERS and USER_INDEX by index. However, USER_INDEX contains pairs of [uid, position]. Popping from USER_INDEX does not update the 'position' values stored inside the remaining pairs, leading to corrupted index mapping.",
    "line": 88,
    "suggestion": "Rebuild the USER_INDEX after removing users, or use a dictionary for USER_INDEX to map uid to record directly."
  },
  {
    "rule_id": "performance-bottleneck",
    "severity": "warning",
    "message": "find_user_position performs a linear search O(N) through a list. This will cause significant performance degradation as the number of users grows.",
    "line": 13,
    "suggestion": "Change USER_INDEX to a dictionary {uid: position} for O(1) lookups."
  },
  {
    "rule_id": "logic-correctness",
    "severity": "warning",
    "message": "The add_friend function modifies a tuple element. While the list inside the tuple (user[3]) is mutable, the tuple itself is not. The line 'USERS[pos] = ...' in mark_inactive shows the author is aware of this, but the overall design of mixing mutable lists inside immutable tuples is inconsistent.",
    "line": 31,
    "suggestion": "Use a class or a dictionary for the user record to allow consistent mutation."
  },
  {
    "rule_id": "naming-conventions",
    "severity": "info",
    "message": "Variable names like 'u', 's', and 'm' are too generic and lack semantic clarity.",
    "line": 61,
    "suggestion": "Rename 'u' to 'user', 's' to 'unique_ages', and 'm' to 'user_map'."
  },
  {
    "rule_id": "software-engineering-standards",
    "severity": "warning",
    "message": "The codebase maintains redundant state for friendships across two different systems: the user record list (user[3]) and the global FRIEND_A/FRIEND_B lists. This violates the 'Single Source of Truth' principle and can lead to data inconsistency.",
    "line": 38,
    "suggestion": "Consolidate friendship data into a single data structure (e.g., an adjacency list)."
  },
  {
    "rule_id": "logic-correctness",
    "severity": "info",
    "message": "get_unique_ages_sorted returns a list from a set, but the list is not explicitly sorted, despite the function name suggesting it should be.",
    "line": 73,
    "suggestion": "Wrap the return value in sorted(): return sorted(list(s))"
  }
]
```