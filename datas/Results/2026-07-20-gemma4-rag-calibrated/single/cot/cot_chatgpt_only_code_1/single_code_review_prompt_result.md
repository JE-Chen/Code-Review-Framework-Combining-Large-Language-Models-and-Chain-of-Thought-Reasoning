This code contains several critical anti-patterns that affect maintainability, performance, and reliability. Below is the professional review.

### 1. Linter & Style Issues (PEP 8)
*   **Naming Conventions:** Python uses `snake_case` for functions and variables. `doStuff`, `processEverything`, and `collectValues` should be `do_stuff`, `process_everything`, and `collect_values`.
*   **Magic Numbers:** The values `3.14159` and `2.71828` are hardcoded. Use `math.pi` and `math.e` for precision and clarity.
*   **Bare Except:** The `except:` block in `processEverything` is too broad. It will catch `KeyboardInterrupt` or `SystemExit`, making the program hard to kill. Use `except ValueError:`.

### 2. Code Smells
*   **The "Arrow" Anti-pattern (Deep Nesting):** The `doStuff` function has 5 levels of nested `if` statements. This is a cognitive burden and highly error-prone.
*   **Global State:** The use of `global total_result` makes the code non-thread-safe and difficult to test. State should be passed as arguments or managed within a class.
*   **Mutable Default Arguments:** In `collectValues(x, bucket=[])`, the list `bucket` is created once at definition time, not at call time. Subsequent calls will append to the same list, leading to unexpected behavior (as seen in your output).
*   **Dead Code:** The `if i or j: pass` block and the `temp1`/`temp2` calculations do nothing and should be removed.
*   **Inefficient Type Checking:** Using `type(item) == int` is discouraged. Use `isinstance(item, int)`.

### 3. Best Practices & Logic
*   **Complexity:** `doStuff` takes 10 arguments, many of which are flags. This is a sign that the function is doing too many things. It should be split into smaller, single-responsibility functions.
*   **Redundant Conversions:** `final_result = float(str(sum))` is an expensive and illogical way to cast a number to a float. Use `float(sum)`.
*   **Performance:** `time.sleep(0.01)` inside a loop significantly slows down processing for no apparent reason.
*   **Summation:** Instead of manually looping to calculate `total`, use the built-in `sum(results)`.

---

### Suggested Refactoring

```python
import math

# Use a class or a wrapper to avoid global variables
class Processor:
    def __init__(self):
        self.total_result = 0

    def calculate_value(self, a, shape, c, flags):
        # Use constants from math module
        x = a * math.pi if a > 10 else a * math.e

        if shape == "square":
            y = c * c
        elif shape == "circle":
            y = math.pi * c * c
        else:
            y = c

        # Flattened logic using a guard-clause style or simplified boolean logic
        d, e, f, g, h = flags
        if not d:
            z = y
        elif not e:
            z = x
        elif not f:
            z = x / y if y != 0 else 0
        elif not g:
            z = x * y
        elif not h:
            z = x - y
        else:
            z = x + y

        self.total_result += z
        return z

    def process_everything(self, data):
        results = []
        for item in data:
            # Simplified input normalization
            try:
                a = int(float(item)) if not isinstance(item, (int, float)) else int(item)
            except (ValueError, TypeError):
                a = 0

            shape = "square" if a % 2 == 0 else "circle"
            # Group flags into a tuple to reduce argument count
            flags = (True, False, True, True, False) 
            
            r = self.calculate_value(a, shape, a, flags)
            results.append(max(0, r))

        return float(sum(results))

def collect_values(x, bucket=None):
    # Fix mutable default argument
    if bucket is None:
        bucket = []
    bucket.append(x)
    return bucket

if __name__ == "__main__":
    data = [1, 2, "3", 4.5, "bad", 7]
    proc = Processor()
    output = proc.process_everything(data)
    
    print(f"Final: {output}")
    print(f"Global total_result: {proc.total_result}")
```

### Summary of Improvements:
1.  **Complexity:** Reduced nesting from 5 levels to 1.
2.  **Safety:** Fixed the `bucket=[]` bug and the bare `except`.
3.  **Performance:** Removed `time.sleep` and replaced manual loops with `sum()`.
4.  **Architecture:** Encapsulated global state into a `Processor` class.
5.  **Readability:** Applied PEP 8 naming and used `math` constants.