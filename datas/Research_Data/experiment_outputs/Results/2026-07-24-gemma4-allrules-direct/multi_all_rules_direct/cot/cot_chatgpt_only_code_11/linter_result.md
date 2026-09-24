```json
[
  {
    "rule_id": "shared-mutable-state",
    "severity": "warning",
    "message": "Global mutable lists (USERS, USER_INDEX, MIXED_LOG, FRIEND_A, FRIEND_B) introduce hidden coupling and make the code difficult to test and reason about.",
    "line": 4,
    "suggestion": "Encapsulate state within a class (e.g., UserManager) and pass instances explicitly."
  },
  {
    "rule_id": "naming-conventions",
    "severity": "info",
    "message": "Variable names like 'u', 's', 'm', and 'i' are too short and not descriptive.",
    "line": 54,
    "suggestion": "Use descriptive names such as 'user', 'unique_ages', 'user_map', and 'index'."
  },
  {
    "rule_id": "single-responsibility",
    "severity": "warning",
    "message": "The function 'find_users_by_age' has multiple responsibilities: filtering users and transforming the result into a map based on a flag.",
    "line": 68,
    "suggestion": "Split into two functions: one for filtering and one for mapping."
  },
  {
    "rule_id": "inconsistent-return-types",
    "severity": "error",
    "message": "The function 'find_users_by_age' returns different types (list or dict) depending on the 'as_map' argument.",
    "line": 75,
    "suggestion": "Ensure the function returns a consistent type or split it into two distinct functions."
  },
  {
    "rule_id": "logic-correctness",
    "severity": "error",
    "message": "The 'remove_young_users' function pops elements from 'USER_INDEX' using the same index as 'USERS', but 'USER_INDEX' is a list of pairs [uid, position]. Popping by index from 'USER_INDEX' does not correctly update the mapping for other users, and the 'position' stored inside the pairs becomes stale.",
    "line": 82,
    "suggestion": "Use a dictionary for USER_INDEX to map UIDs to positions, or rebuild the index after removals."
  },
  {
    "rule_id": "naming-conventions",
    "severity": "info",
    "message": "The function name 'duplicate_users' describes the action but not the intent; it is essentially a clone operation.",
    "line": 65,
    "suggestion": "Rename to 'clone_user_list' or similar."
  },
  {
    "rule_id": "software-engineering-standards",
    "severity": "warning",
    "message": "The code relies heavily on magic indices for tuples (e.g., u[0], u[2], user[3]). This is fragile and reduces readability.",
    "line": 55,
    "suggestion": "Use namedtuples or dataclasses to represent User records."
  }
]
```