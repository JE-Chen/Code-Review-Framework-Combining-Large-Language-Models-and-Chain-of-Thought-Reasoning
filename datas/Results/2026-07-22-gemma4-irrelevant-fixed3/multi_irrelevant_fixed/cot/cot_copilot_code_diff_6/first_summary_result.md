### Code Review

#### 1. Readability & Consistency
- **Formatting**: The code lacks consistent spacing and follows a mix of styles.
- **Language Consistency**: The `print` statements use a mix of English and Traditional Chinese. For a professional codebase, it is recommended to stick to one language (typically English) for logs and console output.

#### 2. Naming Conventions
- **Function Naming**: `functionThatDoesTooMuchAndIsHardToUnderstand` violates standard Python naming conventions (PEP 8). It should use `snake_case` (e.g., `fetch_and_post_data`). Furthermore, the name is self-deprecating rather than descriptive of the function's actual purpose.
- **Variable Naming**: `weirdVariableName` and `r2` are not descriptive. Use names that reflect the content of the variable (e.g., `post_response` or `posts_list_response`).

#### 3. Software Engineering Standards
- **Modularity**: The function violates the Single Responsibility Principle. It performs three distinct network operations (GET single item, GET list, POST item) and handles printing/logging internally. These should be split into smaller, reusable functions.
- **Global State**: The use of `global GLOBAL_SESSION` inside the function is unnecessary as the session is only being read, not reassigned.

#### 4. Logic & Correctness
- **Exception Handling**: 
    - The first `try-except` block catches `Exception`, which is too broad.
    - The second `try-except` block is a "bare except" (`except:`), which is a dangerous practice in Python as it catches `SystemExit` and `KeyboardInterrupt`, making it difficult to stop the program.
- **Error Handling**: The code prints that it "doesn't care" about errors (`錯誤但我不管`). In a production environment, exceptions should be logged properly or handled to allow the system to recover or fail gracefully.

#### 5. Performance & Security
- **Resource Management**: While a `requests.Session()` is used (which is good for performance), there is no timeout specified for the `.get()` or `.post()` calls. This can lead to the application hanging indefinitely if the server does not respond.

#### 6. Documentation & Testing
- **Documentation**: There are no docstrings or comments explaining the purpose of the script or the expected behavior of the functions.
- **Testing**: No unit tests are provided to verify the network interactions or error handling.

---

### Summary of Changes (PR Summary)

- **Key changes**: Introduced a new script `bad_requests.py` to perform GET and POST requests to a placeholder API.
- **Impact scope**: New standalone utility file.
- **Purpose of changes**: Initial implementation of API interaction logic.
- **Risks and considerations**: Current implementation lacks robust error handling and timeout configurations, which may lead to instability in production.
- **Items to confirm**: Reviewer should validate the naming conventions and the appropriateness of the exception handling strategy.