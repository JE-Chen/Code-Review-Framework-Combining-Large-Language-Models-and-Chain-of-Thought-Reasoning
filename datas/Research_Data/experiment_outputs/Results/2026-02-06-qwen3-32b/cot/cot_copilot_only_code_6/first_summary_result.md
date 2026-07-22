### Code Review Summary

- **Key changes**  
  Refactored global configuration to use Flask's built-in config system, added input validation for `/add`, and standardized response formats across all endpoints.

- **Impact scope**  
  Configuration handling and three endpoints (`/add`, `/complex`, `/reset`) affected. Configuration now managed via Flask's config object instead of global dictionary.

- **Purpose of changes**  
  Eliminated global state issues, prevented potential bugs (e.g., non-string payloads in `/add`), and ensured consistent JSON responses. Fixes critical code smells while maintaining existing functionality.

- **Risks and considerations**  
  - Clients sending non-string payloads to `/add` will now receive validation errors (previously silently appended as `None`).  
  - Reset endpoint no longer alters configuration mode (previously set to `"reset"`, which was unused and confusing).  
  - Requires client updates if they relied on silent `None` handling or `"reset"` mode.

- **Items to confirm**  
  1. Verify configuration defaults (e.g., `mode="test"`, `threshold=123`) work as expected in all environments.  
  2. Confirm `/complex` returns consistent JSON (no string returns).  
  3. Ensure reset endpoint behavior aligns with client expectations (no mode mutation).