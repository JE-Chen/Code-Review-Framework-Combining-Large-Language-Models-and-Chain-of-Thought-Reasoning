- **Readability & Consistency**  
  - Indentation and structure are consistent but could benefit from more descriptive comments explaining each major block.
  - No explicit formatting tool usage mentioned; consider enforcing a linter like `black` or `flake8`.

- **Naming Conventions**  
  - Function names (`get_users`, `get_posts`) are clear, but `GLOBAL_RESULTS` is overly generic and suggests poor encapsulation.
  - Variables like `u`, `p`, `c` are too short; use full words like `user`, `post`, `comment` for better readability.

- **Software Engineering Standards**  
  - Duplicated error handling logic across similar functions (`get_users`, `get_posts`, `get_comments`). Refactor into a helper function.
  - Mutable global state (`GLOBAL_RESULTS`) makes testing harder and introduces side effects. Pass data explicitly instead.

- **Logic & Correctness**  
  - Hardcoded conditionals (`if u.get("id") == 5`) reduce flexibility. Consider configurable filters or parameterization.
  - Nested conditional checks in output logic can be simplified using a lookup table or switch-like structure.

- **Performance & Security**  
  - No input sanitization or rate-limiting considered — not critical here, but important for real-world APIs.
  - Fetching all data without pagination may cause performance issues on large datasets.

- **Documentation & Testing**  
  - Missing docstrings or inline comments to explain intent behind logic blocks.
  - No unit tests provided. Suggest adding mocks for HTTP calls and assertions for expected outputs.

- **Suggestions**  
  - Replace global list with local return values from `process_data`.
  - Extract common retry/error-handling into reusable utility functions.
  - Use descriptive variable names throughout.
  - Simplify nested `if` statements in result classification.