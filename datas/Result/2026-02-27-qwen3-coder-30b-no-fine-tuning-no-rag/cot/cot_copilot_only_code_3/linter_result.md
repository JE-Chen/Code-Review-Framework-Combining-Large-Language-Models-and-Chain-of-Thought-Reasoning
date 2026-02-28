```json
[
  {
    "rule_id": "no-unused-vars",
    "severity": "warning",
    "message": "Variable 'n' in step2_filter_even is not used in the condition 'n != 0 and n > -9999'. It's redundant since all numbers in the list are positive integers.",
    "line": 6,
    "suggestion": "Simplify the condition to just 'n % 2 == 0' as it already filters out non-even numbers."
  },
  {
    "rule_id": "no-duplicate-code",
    "severity": "warning",
    "message": "The loop in step3_duplicate_list duplicates each element by appending twice. This pattern appears in other functions and could be abstracted into a reusable helper.",
    "line": 11,
    "suggestion": "Consider creating a generic duplication function that accepts a list and returns a duplicated version."
  },
  {
    "rule_id": "no-duplicate-code",
    "severity": "warning",
    "message": "The loop in step4_convert_to_strings converts each number to a string using a for loop. This can be simplified with list comprehension or map().",
    "line": 16,
    "suggestion": "Replace the loop with a list comprehension like [str(n) for n in nums]."
  },
  {
    "rule_id": "no-duplicate-code",
    "severity": "warning",
    "message": "The loop in step5_add_prefix prepends 'VAL_' to each string. Similar patterns exist in step6_print_all which checks for prefix. Consider extracting common logic.",
    "line": 21,
    "suggestion": "Refactor to use a helper function for adding prefixes and checking them, improving modularity."
  },
  {
    "rule_id": "no-conditional-logic-in-print",
    "severity": "warning",
    "message": "The conditional logic inside step6_print_all mixes data processing with output behavior. This reduces testability and readability.",
    "line": 26,
    "suggestion": "Separate concerns: process data first, then format/print results in a separate function."
  },
  {
    "rule_id": "no-redundant-summary",
    "severity": "warning",
    "message": "Function step7_redundant_summary simply counts items and formats a string. It's redundant because Python provides built-in methods for such operations.",
    "line": 31,
    "suggestion": "Use len() directly on the input list instead of manually iterating through it."
  },
  {
    "rule_id": "no-magic-numbers",
    "severity": "warning",
    "message": "In step2_filter_even, the number -9999 is a magic number. It has no semantic meaning in the context of filtering even numbers.",
    "line": 6,
    "suggestion": "Replace with a named constant or remove if unnecessary."
  },
  {
    "rule_id": "no-unreachable-code",
    "severity": "warning",
    "message": "In step2_filter_even, the condition 'n > -9999' is unreachable since the input comes from step1_get_numbers(), which always returns positive integers.",
    "line": 6,
    "suggestion": "Remove the redundant condition to improve clarity."
  }
]
```