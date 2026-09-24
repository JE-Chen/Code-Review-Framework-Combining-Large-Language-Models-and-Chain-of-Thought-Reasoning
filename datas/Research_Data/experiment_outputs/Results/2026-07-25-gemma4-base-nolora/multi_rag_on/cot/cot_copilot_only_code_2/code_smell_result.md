- Code Smell Type: Magic Numbers
- Problem Location: `NumberProcessor.process` method: `(data * 1234) % 5678 + 9999`
- Detailed Explanation: The numbers `1234`, `5678`, and `9999` are "magic numbers"—hardcoded literals without explained meaning. This makes the business logic opaque and difficult to maintain. If these values need to change or are reused elsewhere, it requires searching and replacing literals across the codebase, which is error-prone.
- Improvement Suggestions: Define these values as named constants at the class level or in a configuration file (e.g., `MULTIPLIER = 1234`, `MODULUS = 5678`, `OFFSET = 9999`).
- Priority Level: Medium

- Code Smell Type: Deeply Nested Conditionals (Arrow Anti-pattern)
- Problem Location: `main()` function, the block starting with `if GLOBAL_CONFIG["flag"]:`
- Detailed Explanation: The code exhibits four levels of nested `if` statements. This "arrow" shape significantly reduces readability and increases cognitive load, making it harder to track the execution flow and the conditions required to reach the inner-most logic.
- Improvement Suggestions: Use "Guard Clauses" to return early or flatten the logic. For example, check `if not GLOBAL_CONFIG["flag"]: print("Flag disabled"); return` at the start to remove one level of indentation for the rest of the block.
- Priority Level: Medium

- Code Smell Type: Inefficient String Concatenation
- Problem Location: `StringProcessor.process` method: `result += ch.upper()` and `result += str(ord(ch))`
- Detailed Explanation: In Python, strings are immutable. Using the `+=` operator inside a loop creates a new string object in every iteration, leading to $O(n^2)$ time complexity relative to the length of the input string. While negligible for small strings, this is a performance bottleneck for larger datasets.
- Improvement Suggestions: Collect the characters in a list and use `"".join(result_list)` at the end of the loop.
- Priority Level: Low