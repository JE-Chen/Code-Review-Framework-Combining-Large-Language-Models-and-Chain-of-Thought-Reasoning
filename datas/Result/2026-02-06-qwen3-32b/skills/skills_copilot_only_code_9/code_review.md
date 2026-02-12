### Diff #1

#### Summary
- **Purpose**: The code fetches user, post, and comment data from a public API, processes it to identify specific patterns (special user with ID 5, long post titles, and email-based comments), and prints results with count-based feedback.
- **Scope**: Limited to a single script with four API-fetching functions (`get_users`, `get_posts`, `get_comments`), a data processor (`process_data`), and a main entry point (`main`). Uses global state (`GLOBAL_RESULTS`) for result accumulation.
- **Plain-language explanation**: This script pulls data from a fake online service, checks for specific user IDs, long post titles, and email formats, collects matching items, and prints them with a summary of how many results were found.

---

#### Linting Issues
- **Global variable misuse**  
  `GLOBAL_RESULTS` is used as a global list without explicit scope handling.  
  *Suggestion*: Replace with local return values and pass results through function parameters.

- **Overly broad exception handling**  
  Functions catch `Exception` instead of specific API-related exceptions (e.g., `requests.exceptions.RequestException`).  
  *Suggestion*: Narrow exception scope to improve error clarity and safety.

- **Magic strings in conditionals**  
  Hardcoded strings like `"Special User: "` and `"Long Post Title: "` appear in `process_data`.  
  *Suggestion*: Extract to constants or configuration for maintainability.

- **Inconsistent string formatting**  
  Mixed use of `+` concatenation (e.g., `"Special User: " + u.get("name")`) instead of f-strings.  
  *Suggestion*: Standardize to f-strings for readability (e.g., `f"Special User: {u.get('name')}"`).

---

#### Code Smells
- **Global state dependency**  
  `GLOBAL_RESULTS` couples `process_data` to a global variable, making the function non-reusable and hard to test.  
  *Why problematic*: Breaks single responsibility principle; changes to `GLOBAL_RESULTS` could cause unexpected side effects.  
  *Recommendation*: Return results from `process_data` and handle printing in `main`.

- **Magic number in condition**  
  Hardcoded `id == 5` in `process_data` (line 30) lacks context.  
  *Why problematic*: Requires code inspection to understand meaning; changes risk breaking logic.  
  *Recommendation*: Define `SPECIAL_USER_ID = 5` at module level.

- **Overly long function**  
  `process_data` (lines 30–47) combines three unrelated checks (users, posts, comments).  
  *Why problematic*: Violates single responsibility; increases cognitive load and error risk.  
  *Recommendation*: Split into `process_special_user`, `process_long_titles`, `process_email_comments`.

- **Inconsistent null handling**  
  Uses `.get("key", "default")` inconsistently (e.g., `p.get("title", "")` vs. `c.get("email", "")`).  
  *Why problematic*: Creates subtle bugs if default values change; reduces readability.  
  *Recommendation*: Standardize to `get(key, default_value)` or use explicit checks.

- **Nesting in `main`**  
  Deeply nested conditionals for result counts (lines 48–54) complicate logic.  
  *Why problematic*: Hard to extend or modify (e.g., adding more count thresholds).  
  *Recommendation*: Replace with a helper function or match-case statement.