1. **Mutable Default Argument**
   - **Issue**: The function `add_item` uses a mutable default argument (`container=[]`). This causes shared state across calls.
   - **Root Cause**: Defaults are evaluated once at function definition time.
   - **Impact**: Unexpected side effects when modifying the default list.
   - **Fix**: Replace with `None` and initialize inside the function.
     ```python
     def add_item(item, container=None):
         if container is None:
             container = []
         container.append(item)
         return container
     ```
   - **Best Practice**: Avoid mutable defaults; use `None` instead.

2. **Global State Mutation**
   - **Issue**: Function `append_global` modifies a global list.
   - **Root Cause**: Hidden dependency on external state.
   - **Impact**: Makes code harder to test and reason about.
   - **Fix**: Pass list as parameter or encapsulate in a class.
   - **Best Practice**: Minimize global mutations.

3. **Input Mutation**
   - **Issue**: Function `mutate_input` alters its input directly.
   - **Root Cause**: Lack of immutability expectation.
   - **Impact**: Surprises callers expecting unchanged inputs.
   - **Fix**: Return a new list instead of mutating input.
     ```python
     def mutate_input(data):
         return [x * 2 for x in data]
     ```
   - **Best Practice**: Prefer immutable operations unless explicitly documented otherwise.

4. **Deeply Nested Conditionals**
   - **Issue**: Complex nesting reduces readability.
   - **Root Cause**: Lack of early exits or helper logic.
   - **Impact**: Harder to debug and extend.
   - **Fix**: Flatten with early returns or helper functions.
     ```python
     def nested_conditions(x):
         if x <= 0:
             return "zero" if x == 0 else "negative"
         elif x < 10:
             return "small even positive" if x % 2 == 0 else "small odd positive"
         elif x < 100:
             return "medium positive"
         else:
             return "large positive"
     ```
   - **Best Practice**: Reduce nesting via guard clauses or refactoring.

5. **Broad Exception Handling**
   - **Issue**: Catches generic `Exception`.
   - **Root Cause**: Masks unexpected errors.
   - **Impact**: Obfuscates real problems.
   - **Fix**: Catch specific exceptions.
     ```python
     def risky_division(a, b):
         try:
             return a / b
         except ZeroDivisionError:
             return None
     ```
   - **Best Practice**: Handle known exceptions explicitly.

6. **Inconsistent Return Types**
   - **Issue**: Function returns mixed types (`int`, `str`).
   - **Root Cause**: No consistency enforced.
   - **Impact**: Caller confusion and runtime errors.
   - **Fix**: Enforce uniform return type.
     ```python
     def inconsistent_return(flag):
         return str(42) if flag else "forty-two"
     ```
   - **Best Practice**: Always return predictable types.

7. **Side Effect in List Comprehension**
   - **Issue**: Side effect (print) in comprehension.
   - **Root Cause**: Misuse of comprehensions for non-collection purposes.
   - **Impact**: Confusing behavior and reduced clarity.
   - **Fix**: Use explicit loops.
     ```python
     for i in range(3):
         print(i)
     ```
   - **Best Practice**: Keep comprehensions pure.

8. **Use of `eval()`**
   - **Issue**: Security vulnerability due to dynamic code execution.
   - **Root Cause**: Unsafe evaluation mechanism.
   - **Impact**: Potential remote code injection.
   - **Fix**: Avoid `eval()`; prefer safe alternatives.
   - **Best Practice**: Never allow arbitrary code execution.