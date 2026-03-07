[
  {
    "rule_id": "invalid-index-storage",
    "severity": "error",
    "message": "Index stored in USER_INDEX is the index at creation time, but removals change the current index. This will cause index out of bounds in user access.",
    "line": 23,
    "suggestion": "Use a dictionary to map uid to current index and update on removal."
  },
  {
    "rule_id": "duplicate-uid",
    "severity": "warning",
    "message": "add_user does not check for duplicate uids, which may lead to inconsistent state.",
    "line": 22,
    "suggestion": "Check for existing uid in USERS before appending."
  },
  {
    "rule_id": "unmaintainable-data-structure",
    "severity": "warning",
    "message": "Using two global lists (FRIEND_A, FRIEND_B) for friendship is error-prone and hard to maintain.",
    "line": 35,
    "suggestion": "Replace with a dictionary mapping uid to list of friends."
  },
  {
    "rule_id": "missing-docstring",
    "severity": "info",
    "message": "Function create_user_record lacks a docstring.",
    "line": 8,
    "suggestion": "Add a docstring describing the parameters and return value."
  },
  {
    "rule_id": "unsorted-unique-ages",
    "severity": "error",
    "message": "Function returns unsorted list of unique ages despite name implying sorted.",
    "line": 65,
    "suggestion": "Sort the list of unique ages before returning."
  },
  {
    "rule_id": "dead-code",
    "severity": "info",
    "message": "Function build_age_map is unused and returns a list instead of a map.",
    "line": 49,
    "suggestion": "Remove unused function or adjust return type to match name."
  },
  {
    "rule_id": "negative-age",
    "severity": "warning",
    "message": "Setting age to -1 to mark inactive is non-standard and confusing.",
    "line": 85,
    "suggestion": "Use a separate field to mark inactive instead of negative age."
  }
]