- **Naming Conventions**:  
  `ANOTHER_GLOBAL` is vague and uninformative; rename to `BASE_URL` for clarity.  
  `weirdVariableName` is cryptic and unhelpful; rename to `post_response` to describe its purpose.

- **Function Design**:  
  `functionThatDoesTooMuchAndIsHardToUnderstand` violates single-responsibility principle. Split into smaller functions (e.g., `fetch_post()`, `create_post()`) for modularity and testability.

- **Error Handling**:  
  Broad `except Exception` swallows all errors without context. Replace with specific exception types (e.g., `requests.exceptions.RequestException`) and meaningful logging.

- **Redundant Logic**:  
  `len(r2.text)` is unnecessary for success validation; rely solely on `response.status_code == 200` for clarity and reliability.

- **Global State**:  
  `GLOBAL_SESSION` creates tight coupling and testability issues. Pass session as a dependency instead of using a global.