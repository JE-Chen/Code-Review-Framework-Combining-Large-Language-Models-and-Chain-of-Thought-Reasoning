### Code Review Report

#### 1. Readability & Consistency
* **Deep Nesting:** The `doStuff` function contains deeply nested `if` statements (up to 5 levels), which severely hinders readability and maintainability.
* **Useless Operations:** `temp1` and `temp2` are redundant calculations that simply return the original value of `z`.
* **Dead Code:** The `if i or j: pass` block serves no purpose and should be removed.

#### 2. Naming Conventions
* **Non-Descriptive Names:** Variables like `a, b, c, d, e, f, g, h, i, j` and `x, y, z` provide no semantic meaning. Use descriptive names (e.g., `radius`, `shape_type`).
* **Generic Function Names:** `doStuff` and `processEverything` are too vague. Rename them to reflect their actual business logic (e.g., `calculate_area_metric`).

#### 3. Software Engineering Standards
* **Single Responsibility Principle:** `doStuff` handles calculation, state mutation (`global`), and I/O (`time.sleep`). These should be separated.
* **Input Mutation/State:** The use of `global total_result` creates hidden coupling and makes the code difficult to test or run in parallel.
* **Dangerous Defaults:** `collectValues(x, bucket=[])` uses a mutable default argument. The list persists across calls, leading to unexpected behavior (as seen in the `__main__` output).

#### 4. Logic & Correctness
* **Type Checking:** `type(item) == int` is less flexible than `isinstance(item, int)`.
* **Bare Exception:** The `except:` block in `processEverything` catches all exceptions, including keyboard interrupts, which is a bad practice.
* **Type Conversion:** `float(str(sum))` is an inefficient and circuitous way to cast a value to a float.

#### 5. Performance & Security
* **Unnecessary Delay:** `time.sleep(0.01)` inside a loop introduces a significant, artificial performance bottleneck.
* **Efficiency:** The final sum in `processEverything` is calculated by iterating over the `results` list manually; `sum(results)` is the standard Pythonic approach.

#### 6. Documentation & Testing
* **Missing Documentation:** There are no docstrings or comments explaining the purpose of the complex logic in `doStuff`.
* **Lack of Tests:** No unit tests are provided to verify the logic of the different shape calculations or data parsing.

---

### Concise Improvement Suggestions
* **Refactor `doStuff`:** Flatten the nested `if` statements using guard clauses or a mapping strategy.
* **Fix Mutable Defaults:** Change `bucket=[]` to `bucket=None` and initialize as `if bucket is None: bucket = []`.
* **Remove Global State:** Pass `total_result` as an argument or encapsulate the logic within a class.
* **Clean up Naming:** Rename variables from single letters to descriptive nouns (e.g., `a` $\rightarrow$ `value`).
* **Optimize Casting:** Replace `float(str(sum))` with `float(sum)`.