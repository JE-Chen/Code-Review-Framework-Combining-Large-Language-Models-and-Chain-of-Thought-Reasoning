```json
[
  {
    "rule_id": "naming-conventions",
    "severity": "warning",
    "message": "Global variables USERS, USER_INDEX, MIXED_LOG, FRIEND_A, and FRIEND_B are named like constants (UPPER_CASE) but are mutated throughout the program.",
    "line": 4,
    "suggestion": "Use lower_case_with_underscores for mutable global variables."
  },
  {
    "rule_id": "software-engineering-standards",
    "severity": "error",
    "message": "The use of tuples for user records (e.g., user[0], user[2]) creates 'magic numbers' and makes the code fragile and hard to maintain.",
    "line": 7,
    "suggestion": "Use a namedtuple, dataclass, or a class to define the User structure."
  },
  {
    "rule_id": "logic-correctness",
    "severity": "error",
    "message": "The remove_young_users function pops elements from USERS and USER_INDEX by index, but it does not update the positions stored inside the USER_INDEX values, leading to corrupted index mapping.",
    "line": 88,
    "suggestion": "Rebuild the index or use a dictionary for O(1) lookups and deletions."
  },
  {
    "rule_id": "performance-bottleneck",
    "severity": "warning",
    "message": "find_user_position performs a linear search O(N) on USER_INDEX, which is inefficient for frequent lookups.",
    "line": 14,
    "suggestion": "Use a dictionary for USER_INDEX to achieve O(1) lookup time."
  },
  {
    "rule_id": "logic-correctness",
    "severity": "warning",
    "message": "get_unique_ages_sorted returns a list from a set, but the list is not explicitly sorted, despite the function name suggesting it should be.",
    "line": 68,
    "suggestion": "Wrap the return value in sorted(), e.g., return sorted(list(s))."
  },
  {
    "rule_id": "software-engineering-standards",
    "severity": "info",
    "message": "The build_age_map function creates an intermediate list of tuples and then iterates over it to create a list of dictionaries, which is redundant.",
    "line": 58,
    "suggestion": "Use a list comprehension: return [{'id': uid, 'age': age} for uid, age in age_map.items()]."
  },
  {
    "rule_id": "logic-correctness",
    "severity": "warning",
    "message": "The add_friend function modifies a tuple element (the list at index 3) in place. While lists are mutable, the overall record is a tuple, which is inconsistent with the mark_inactive function that replaces the whole tuple.",
    "line": 31,
    "suggestion": "Consistently use mutable objects (like classes) or immutable updates."
  }
]
```