Based on the provided global rules and the specific prompt requirements, here is the code review for the provided source code.

### Code Review Summary
The codebase suffers from significant software engineering issues, primarily regarding **data integrity**, **state management**, and **time/space complexity**. The use of global variables and disconnected parallel lists (`FRIEND_A`, `FRIEND_B`) creates a fragile system where data can easily become desynchronized.

---

### Linter Messages

```json
[
  {
    "rule_id": "global-state-mutation",
    "severity": "error",
    "message": "Extensive use of global variables (USERS, USER_INDEX, MIXED_LOG, FRIEND_A, FRIEND_B) makes the code difficult to test and prone to side-effect bugs.",
    "line": 4,
    "suggestion": "Encapsulate state within a UserManagement class or pass state objects as arguments to functions."
  },
  {
    "rule_id": "data-integrity-risk",
    "severity": "error",
    "message": "Parallel lists FRIEND_A and FRIEND_B are used to track relationships. If one is modified without the other, the data becomes corrupted.",
    "line": 35,
    "suggestion": "Use a dictionary or a dedicated Relationship object to store mappings."
  },
  {
    "rule_id": "incorrect-indexing-logic",
    "severity": "error",
    "message": "remove_young_users pops elements from USERS and USER_INDEX, but does not update the positions stored inside USER_INDEX for remaining users. This invalidates find_user_position.",
    "line": 79,
    "suggestion": "Avoid using index-based pointers in a list that allows deletions; use a dictionary for O(1) lookup by UID."
  },
  {
    "rule_id": "tuple-immutability-error",
    "severity": "error",
    "message": "The function add_friend attempts to modify a tuple (user[3].append), which will fail if the tuple is treated as immutable, or creates confusion as tuples should not contain mutable lists for modifications.",
    "line": 28,
    "suggestion": "Use a Data Class or a Dictionary for user records instead of tuples."
  },
  {
    "rule_id": "performance-bottleneck",
    "severity": "warning",
    "message": "find_user_position performs a linear scan O(N). In a large dataset, this significantly degrades performance.",
    "line": 14,
    "suggestion": "Convert USER_INDEX to a dictionary for O(1) lookup."
  },
  {
    "rule_id": "semantic-naming",
    "severity": "warning",
    "message": "Variable names like 's', 'u', 'm', and 'temp' are non-descriptive.",
    "line": 61,
    "suggestion": "Use descriptive names like 'unique_ages', 'user', and 'user_map'."
  },
  {
    "rule_id": "logic-redundancy",
    "severity": "info",
    "message": "build_age_map creates a dictionary only to immediately convert it into a list of dictionaries, which is redundant.",
    "line": 54,
    "suggestion": "Generate the list of dictionaries directly from the USERS list."
  },
  {
    "rule_id": "incorrect-return-type",
    "severity": "warning",
    "message": "get_unique_ages_sorted returns a list from a set, but it is not actually sorted, despite the function name.",
    "line": 64,
    "suggestion": "Wrap the return value in sorted(): return sorted(list(s))."
  },
  {
    "rule_id": "memory-leak-risk",
    "severity": "info",
    "message": "MIXED_LOG stores references to the same user records as USERS. If a user is 'removed' from USERS, they persist in MIXED_LOG, potentially preventing garbage collection.",
    "line": 23,
    "suggestion": "Clarify if MIXED_LOG is intended to be a historical archive or a mirror."
  }
]
```