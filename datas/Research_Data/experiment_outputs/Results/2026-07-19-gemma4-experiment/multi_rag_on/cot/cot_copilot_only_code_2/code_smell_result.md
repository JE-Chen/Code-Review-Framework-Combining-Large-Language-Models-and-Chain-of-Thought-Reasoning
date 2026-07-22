- Code Smell Type: Magic Numbers
- Problem Location: `NumberProcessor.process` method: `(data * 1234) % 5678 + 9999`
- Detailed Explanation: The numbers `1234`, `5678`, and `9999` are used without any explanation or named constants. This makes the business logic opaque and difficult to maintain; a developer cannot tell if these values are specific constants, coefficients, or arbitrary placeholders.
- Improvement Suggestions: Define these values as named constants at the class level or in a configuration file (e.g., `MULTIPLIER = 1234`, `MODULUS = 5678`, `OFFSET = 9999`).
- Priority Level: Medium

- Code Smell Type: Deeply Nested Conditionals (Arrow Anti-pattern)
- Problem Location: `main()` function, the block starting with `if GLOBAL_CONFIG["flag"]:`
- Detailed Explanation: The code uses four levels of nested `if` statements. This increases cognitive load, makes the logic harder to follow, and complicates the addition of new conditions. It creates a "pyramid" shape that is a classic sign of poor readability.
- Improvement Suggestions: Use "Guard Clauses" to return or continue early. For example, start with `if not GLOBAL_CONFIG["flag"]: print("Flag disabled"); return`. This flattens the structure and makes the "happy path" easier to trace.
- Priority Level: Medium

- Code Smell Type: Inefficient String Concatenation
- Problem Location: `StringProcessor.process` loop: `result += ch.upper()` and `result += str(ord(ch))`
- Detailed Explanation: In Python, strings are immutable. Using `+=` inside a loop creates a new string object in every iteration, leading to $O(n^2)$ time complexity relative to the string length. While negligible for small strings, it is a performance bottleneck for larger inputs.
- Improvement Suggestions: Collect the characters in a list and use `"".join(result_list)` at the end of the loop.
- Priority Level: Low