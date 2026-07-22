```json
[
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Global variables 'USERS', 'USER_INDEX', 'MIXED_LOG', 'FRIEND_A', and 'FRIEND_B' are named like constants (UPPER_CASE) but are mutated throughout the program.",
    "line": 4,
    "suggestion": "Use snake_case for mutable global variables or encapsulate them within a class."
  },
  {
    "rule_id": "software-engineering-standard",
    "severity": "error",
    "message": "The use of tuples for user records (e.g., user[0], user[2]) makes the code fragile and difficult to maintain. Index-based access lacks semantic meaning.",
    "line": 7,
    "suggestion": "Use a namedtuple, dataclass, or a dictionary to represent user records."
  },
  {
    "rule_id": "logic-correctness",
    "severity": "error",
    "message": "The 'remove_young_users' function pops elements from 'USER_INDEX' using the same index as 'USERS', but 'USER_INDEX' contains [uid, position] pairs, not just uids. This will cause the index to drift and eventually lead to incorrect lookups or IndexError.",
    "line": 88,
    "suggestion": "Rebuild the index or use a dictionary for USER_INDEX to allow O(1) removal and lookup."
  },
  {
    "rule_id": "performance-bottleneck",
    "severity": "warning",
    "message": "The 'find_user_position' function performs a linear search O(N) on 'USER_INDEX'.",
    "line": 13,
    "suggestion": "Change 'USER_INDEX' to a dictionary {uid: position} for O(1) lookup."
  },
  {
    "rule_id": "logic-correctness",
    "severity": "warning",
    "message": "The 'get_unique_ages_sorted' function claims to be 'sorted' in its name, but it returns a list cast from a set, which does not guarantee order.",
    "line": 66,
    "suggestion": "Wrap the return value in sorted(): return sorted(list(s))."
  },
  {
    "rule_id": "software-engineering-standard",
    "severity": "info",
    "message": "The 'build_age_map' function contains redundant steps: it creates a dictionary, converts it to a list of items, and then iterates again to create a list of dictionaries.",
    "line": 54,
    "suggestion": "Use a list comprehension: return [{'id': u[0], 'age': u[2]} for u in USERS]."
  },
  {
    "rule_id": "logic-correctness",
    "severity": "error",
    "message": "The 'add_friend' function modifies a tuple element (the list at index 3) in place, but 'mark_inactive' replaces the entire tuple. This inconsistency in state management can lead to bugs.",
    "line": 31,
    "suggestion": "Use a mutable object (like a class or dict) for user records instead of tuples."
  }
]
```