### Diff #1

#### Summary
This PR introduces a simple state management system using a global dictionary called `GLOBAL_STATE`. The code includes several functions that manipulate this state, such as initializing data, incrementing counters, toggling flags, processing items based on certain conditions, and resetting the state.

Affected files: `script.py`

#### Linting Issues
- **PEP8 Compliance**: 
  - Lines are too long (e.g., lines 4-5, 6-7, etc.). Consider breaking them into multiple lines.
  - Function names could be more descriptive (e.g., `process_items`).
  
- **Unused Imports**: No unused imports were found in this snippet.

Suggested Corrections:
```python
# Break long lines
GLOBAL_STATE = {
    "counter": 0,
    "data": [],
    "mode": "default",
    "threshold": 77,
    "flag": False
}
```
Rename functions like `process_items` to something more descriptive.

#### Code Smells
- **Global State Management**: Using a global dictionary (`GLOBAL_STATE`) can lead to difficult-to-maintain and test code. It violates the Single Responsibility Principle and makes it hard to reason about side effects.
- **Lack of Encapsulation**: Functions directly modify the global state without encapsulating the logic inside classes or objects.
- **Hardcoded Logic**: The behavior of `process_items` depends on the values in `GLOBAL_STATE`, which makes the function tightly coupled and harder to reuse.

Recommendations:
- Refactor the code into a class-based approach where the state is encapsulated within an instance.
- Use methods within the class to perform operations instead of modifying global state directly.
- Consider using dependency injection to pass state to functions rather than relying on global variables.