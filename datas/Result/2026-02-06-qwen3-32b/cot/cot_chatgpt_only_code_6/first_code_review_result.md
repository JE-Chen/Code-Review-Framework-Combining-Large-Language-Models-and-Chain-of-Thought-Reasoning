- **Readability & Consistency**  
  Global variables (`USERS`, `REQUEST_LOG`, `LAST_RESULT`) create hidden dependencies and reduce testability. Avoid global state where possible.  
  Inconsistent string building in `/stats` endpoint: use `jsonify` instead of manual string concatenation.

- **Naming Conventions**  
  `LAST_RESULT` is ambiguous—rename to `last_operation_result` or eliminate entirely (global state is problematic).  
  Endpoint `/doStuff` lacks semantic meaning—rename to `/calculate` or similar.

- **Software Engineering**  
  Duplicate logging logic across endpoints (e.g., `REQUEST_LOG` append in `POST`, `PUT`, `DELETE`). Extract into a reusable helper function.  
  Input validation is incomplete (e.g., `min_age` in `GET` assumes valid integer; `age` in `PUT` can be `None`).

- **Logic & Correctness**  
  `min_age` in `GET` endpoint crashes if client sends non-integer (e.g., `"min_age=abc"`). Add input validation.  
  `PUT` endpoint silently accepts `age=None` if omitted—should require `age` field or reject with 400.

- **Documentation**  
  Missing docstrings for all routes and helper functions. Add brief descriptions of purpose and expected inputs.

- **Security**  
  No validation for numeric fields (e.g., `age` in `POST`/`PUT`). Ensure inputs are integers (not strings) to prevent type errors.  
  Global state (`USERS`, `REQUEST_LOG`) is vulnerable to race conditions in concurrent requests. Not critical for demo, but a pattern to avoid.