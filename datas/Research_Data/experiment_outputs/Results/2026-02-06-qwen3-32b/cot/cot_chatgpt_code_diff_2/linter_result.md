[
  {
    "rule_id": "bad-naming",
    "severity": "warning",
    "message": "Function name 'do_everything' is non-descriptive and does multiple unrelated tasks.",
    "line": 24,
    "suggestion": "Rename to a specific action and split into separate functions."
  },
  {
    "rule_id": "logic-bug",
    "severity": "error",
    "message": "Velocity change is applied for any keydown event, not tied to the specific key pressed.",
    "line": 26,
    "suggestion": "Handle velocity change only for the pressed key (if intended) or remove random velocity change."
  },
  {
    "rule_id": "logic-bug",
    "severity": "error",
    "message": "Score update is only triggered by events, causing it to not update when no events occur.",
    "line": 33,
    "suggestion": "Move score update to the main loop."
  },
  {
    "rule_id": "logic-bug",
    "severity": "warning",
    "message": "Color update is only triggered by events, causing it to not update consistently every frame.",
    "line": 36,
    "suggestion": "Move color update to the main loop."
  },
  {
    "rule_id": "redundant-code",
    "severity": "warning",
    "message": "Redundant use of math.sqrt for absolute value.",
    "line": 43,
    "suggestion": "Replace with abs(STATE['velocity'])."
  },
  {
    "rule_id": "inconsistent-logic",
    "severity": "warning",
    "message": "Down movement uses 'STATE['velocity'] or 1', which may cause unexpected movement when velocity is zero.",
    "line": 47,
    "suggestion": "Use abs(STATE['velocity']) for consistent movement."
  },
  {
    "rule_id": "missing-docstring",
    "severity": "info",
    "message": "Function lacks a docstring explaining its purpose and behavior.",
    "line": 24,
    "suggestion": "Add a docstring to the function."
  },
  {
    "rule_id": "missing-docstring",
    "severity": "info",
    "message": "Function lacks a docstring explaining its purpose and behavior.",
    "line": 39,
    "suggestion": "Add a docstring to the function."
  },
  {
    "rule_id": "missing-docstring",
    "severity": "info",
    "message": "Function lacks a docstring explaining its purpose and behavior.",
    "line": 53,
    "suggestion": "Add a docstring to the function."
  }
]