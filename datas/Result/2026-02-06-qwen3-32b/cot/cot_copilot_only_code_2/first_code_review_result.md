- **Inefficient String Handling in `StringProcessor`**  
  String concatenation (`result += ...`) inside a loop creates O(n²) performance due to immutable strings. Replace with list accumulation and `join()`:  
  ```python
  # Before
  result = ""
  for ch in data:
      result += ...  # Inefficient
  
  # After
  chars = []
  for ch in data:
      chars.append(ch.upper() if ch.isalpha() else str(ord(ch)))
  return ''.join(chars)
  ```

- **Global Configuration Violates Modularity**  
  `GLOBAL_CONFIG` is a mutable global variable, complicating testing and state management. Inject configuration via constructor or function parameters instead.

- **Missing Documentation**  
  Classes and methods lack docstrings. Add brief descriptions for clarity (e.g., `StringProcessor.process` should note it converts non-alphabetic chars to ASCII codes).

- **Ambiguous Variable Names**  
  `ch` (short for "character") is acceptable in tight loops, but `val` in `main()` is too generic. Rename to `input_value` for self-documenting code.

- **Potential Pipeline Mismatch Risk**  
  `StringProcessor` returns a string of digits (e.g., `"495051"`), which may break `NumberProcessor` (expects integers). Add explicit type checks or clarify pipeline contract in documentation.