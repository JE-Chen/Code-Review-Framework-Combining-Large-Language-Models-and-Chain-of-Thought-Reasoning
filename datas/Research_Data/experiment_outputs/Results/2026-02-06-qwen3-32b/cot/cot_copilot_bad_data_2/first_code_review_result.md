- **Security Risk**: `unsafe_eval` uses `eval()`, which executes arbitrary code from user input. This is a critical security vulnerability. Replace with safe alternatives or remove entirely.
  
- **Hidden Global Dependency**: `secret_behavior` relies on global `hidden_flag` instead of explicit parameters. This makes behavior unpredictable and breaks testability. Pass `use_double` as a parameter instead.

- **Implicit Truthiness**: `check_value` uses `if val:` which fails for falsy values like `0`, `[]`, or `None`. Replace with explicit checks (e.g., `if val is not None and val != 0`).

- **I/O in Validation Logic**: `process_user_input` mixes validation with side-effect printing. Move I/O to the caller for testability and reusability.

- **Input Mutation**: `risky_update` mutates the input dictionary (`data`). Return a new dictionary instead to avoid unexpected side effects.

- **Meaningless Naming**: Function `f(x)` has an uninformative name. Rename to reflect its purpose (e.g., `calculate_special_value`).

- **Global State**: `global_config` is mutable and used across functions. Replace with dependency injection (pass config as parameter) to improve testability.