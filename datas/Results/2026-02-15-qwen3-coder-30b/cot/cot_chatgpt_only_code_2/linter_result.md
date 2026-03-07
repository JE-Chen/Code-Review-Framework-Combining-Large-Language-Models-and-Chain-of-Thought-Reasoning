[
  {
    "rule_id": "no-unused-vars",
    "severity": "warning",
    "message": "Variable 'temp' is assigned but never used.",
    "line": 33,
    "suggestion": "Remove unused variable 'temp'."
  },
  {
    "rule_id": "no-implicit-globals",
    "severity": "error",
    "message": "Global variable '_cache' is used without explicit declaration.",
    "line": 25,
    "suggestion": "Declare '_cache' as a module-level constant or use a proper caching mechanism."
  },
  {
    "rule_id": "no-duplicate-case",
    "severity": "warning",
    "message": "Duplicate condition in loop when checking user eligibility.",
    "line": 41,
    "suggestion": "Simplify the filtering logic by combining conditions."
  },
  {
    "rule_id": "no-unnecessary-type-conversion",
    "severity": "warning",
    "message": "Unnecessary conversion of float to string and back to float.",
    "line": 54,
    "suggestion": "Remove redundant type conversion."
  },
  {
    "rule_id": "no-magic-numbers",
    "severity": "warning",
    "message": "Magic number '0.7' used in random selection logic.",
    "line": 66,
    "suggestion": "Replace magic number with named constant."
  },
  {
    "rule_id": "no-hardcoded-strings",
    "severity": "warning",
    "message": "Hardcoded string 'ACTIVE' used directly in conditional.",
    "line": 77,
    "suggestion": "Define status strings as constants."
  },
  {
    "rule_id": "no-undefined-variables",
    "severity": "error",
    "message": "Variable 'users' may be undefined if file does not exist.",
    "line": 17,
    "suggestion": "Ensure all execution paths properly initialize variables."
  }
]