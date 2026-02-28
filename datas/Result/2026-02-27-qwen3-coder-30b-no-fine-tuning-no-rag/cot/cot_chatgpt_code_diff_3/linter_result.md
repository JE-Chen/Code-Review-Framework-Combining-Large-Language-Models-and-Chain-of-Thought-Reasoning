```json
[
  {
    "rule_id": "no-global-variables",
    "severity": "error",
    "message": "Usage of global variable 'GLOBAL_THING' reduces modularity and testability.",
    "line": 13,
    "suggestion": "Refactor 'GLOBAL_THING' into a class member or pass as a parameter."
  },
  {
    "rule_id": "no-unused-vars",
    "severity": "warning",
    "message": "Variable 'layout' is assigned but not used in the scope.",
    "line": 31,
    "suggestion": "Remove unused variable 'layout' or use it appropriately."
  },
  {
    "rule_id": "no-magic-numbers",
    "severity": "warning",
    "message": "Magic number '777' used for timer interval; consider defining as a named constant.",
    "line": 42,
    "suggestion": "Define '777' as a named constant like 'DEFAULT_TIMER_INTERVAL_MS'."
  },
  {
    "rule_id": "no-magic-numbers",
    "severity": "warning",
    "message": "Magic number '0.1' used for sleep duration; consider defining as a named constant.",
    "line": 29,
    "suggestion": "Define '0.1' as a named constant like 'CLICK_DELAY_SECONDS'."
  },
  {
    "rule_id": "no-magic-numbers",
    "severity": "warning",
    "message": "Magic number '5' used in click count modulo check; consider using a named constant.",
    "line": 25,
    "suggestion": "Define '5' as a named constant like 'SLOW_CLICK_THRESHOLD'."
  },
  {
    "rule_id": "no-magic-numbers",
    "severity": "warning",
    "message": "Magic number '7' used in periodic logic; consider defining as a named constant.",
    "line": 48,
    "suggestion": "Define '7' as a named constant like 'EVENT_TRIGGER_INTERVAL'."
  },
  {
    "rule_id": "no-magic-numbers",
    "severity": "warning",
    "message": "Magic number '0.3' used in probability check; consider using a named constant.",
    "line": 44,
    "suggestion": "Define '0.3' as a named constant like 'BUTTON_TEXT_CHANGE_PROBABILITY'."
  },
  {
    "rule_id": "no-sync-in-event-loop",
    "severity": "error",
    "message": "Use of 'time.sleep()' inside event handler may block UI updates.",
    "line": 29,
    "suggestion": "Replace 'time.sleep()' with non-blocking alternatives such as QTimer."
  },
  {
    "rule_id": "no-duplicated-code",
    "severity": "warning",
    "message": "Similar logic appears in 'handle_click' and 'do_periodic_stuff'; could be refactored.",
    "line": 25,
    "suggestion": "Extract shared logic into a helper method to reduce duplication."
  },
  {
    "rule_id": "no-hardcoded-strings",
    "severity": "warning",
    "message": "Hardcoded strings like 'Click maybe', 'Don't click', etc., should be externalized.",
    "line": 45,
    "suggestion": "Move string literals into constants or resource files for better maintainability."
  }
]
```