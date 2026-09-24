- Code Smell Type: Deeply Nested Conditional Logic
- Problem Location: `main()` function, specifically the block starting with `if GLOBAL_CONFIG["flag"]:`
- Detailed Explanation: The code contains four levels of nested `if` statements. This increases cognitive load, makes the logic harder to follow, and complicates future modifications. It violates the RAG rule regarding deeply nested conditional logic.
- Improvement Suggestions: Use guard clauses to handle negative cases early and return or continue, or flatten the logic by combining conditions using `and`. For example:
  ```python
  if not GLOBAL_CONFIG["flag"]:
      print("Flag disabled")
      return

  if val <= 5:
      print("Value too small")
      return
  # ... and so on
  ```
- Priority Level: Medium

- Code Smell Type: Magic Numbers
- Problem Location: `NumberProcessor.process` method: `(data * 1234) % 5678 + 9999`
- Detailed Explanation: The numbers `1234`, `5678`, and `9999` are hard-coded constants without any explanation of their purpose or origin. This makes the business logic opaque and difficult to maintain or update.
- Improvement Suggestions: Define these values as named constants at the class or module level (e.g., `MULTIPLIER = 1234`, `MODULUS = 5678`, `OFFSET = 9999`) to provide semantic meaning.
- Priority Level: Low

- Code Smell Type: Shared Mutable State (Global Variable)
- Problem Location: `GLOBAL_CONFIG = { ... }`
- Detailed Explanation: The use of a global dictionary for configuration introduces hidden coupling. Any part of the program can mutate this state, making the behavior of `main()` dependent on the global environment, which hinders testability and predictability.
- Improvement Suggestions: Encapsulate configuration in a dedicated `Config` class or pass the configuration object explicitly as a parameter to the functions that require it.
- Priority Level: Low