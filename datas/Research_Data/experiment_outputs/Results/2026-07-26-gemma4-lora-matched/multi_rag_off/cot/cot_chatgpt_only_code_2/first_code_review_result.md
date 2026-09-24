### Code Review

**1. Readability & Consistency**
* **Naming Conventions:** Several functions use `camelCase` (`loadAndProcessUsers`, `calculateAverage`, `mainProcess`), which violates PEP 8 standards for Python (should be `snake_case`).
* **Dead Code:** There is a commented-out `if/else` block in `formatUser` that should be removed to keep the codebase clean.

**2. Software Engineering Standards**
* **Resource Management:** In `loadAndProcessUsers`, the file is opened and closed manually (`f = open(...)` / `f.close()`). Use a `with open(...) as f:` block to ensure the file is closed even if an exception occurs.
* **Redundant Logic:** The loop that copies `raw` into `temp` is unnecessary; you can iterate over `raw` directly.
* **Type Consistency:** `getTopUser` returns inconsistent types (sometimes a `User` object, sometimes a `dict`, sometimes `None`). This forces the caller to use `isinstance` checks, increasing complexity and fragility.

**3. Logic & Correctness**
* **Bare Except:** The `try...except:` block in `loadAndProcessUsers` catches all exceptions (including `KeyboardInterrupt`). It should specify `json.JSONDecodeError`.
* **Redundant Casting:** In `calculateAverage`, `avg = float(str(avg))` is redundant and inefficient; the result of division is already a float.

**4. Performance & Security**
* **Input Validation:** `loadAndProcessUsers` does not validate that `raw` is actually a list after `json.loads()`. If the JSON file contains a dictionary or a string, the subsequent `for r in raw` loop will crash or behave unexpectedly.

**Suggested Improvements**
* Rename functions to `load_and_process_users`, `calculate_average`, and `main_process`.
* Use `with open(DATA_FILE, "r") as f:` for file handling.
* Standardize `getTopUser` to always return a `User` object or `None`.
* Replace the bare `except:` with `except json.JSONDecodeError:`.
* Remove the redundant `temp` list and the `float(str(avg))` cast.