### Code Review

**Logic & Correctness**
* **Mutable Default Argument:** `process_items(items=[])` uses a mutable list as a default. This will persist across function calls, leading to unexpected behavior. Use `items=None` and initialize inside the function.
* **Security Risk:** `eval(f"{x} * {x}")` in `expensive_compute` is a critical security vulnerability (code injection). Use standard multiplication `x * x`.
* **Incorrect List Comprehension:** `[results.append(cache[item])]` uses a list comprehension for a side effect. Use a simple `results.append(cache[item])` call.

**Performance & Security**
* **Global State:** `cache` and `results` are global variables. This makes the code non-thread-safe and difficult to test. Pass these as arguments or encapsulate them in a class.
* **Inefficient Loop:** `time.sleep(0.01)` inside the loop introduces an artificial bottleneck. If this is for rate limiting, it should be configurable; otherwise, it should be removed.

**Software Engineering Standards**
* **Exception Handling:** `except Exception: return 0` in `expensive_compute` is too broad. It masks all errors (including `KeyboardInterrupt` or `SyntaxError` from `eval`) and returns a magic number (`0`), which could be a valid result.
* **Modularity:** `process_items` modifies the global `results` list and returns it, creating a side effect that makes the function's behavior unpredictable.

**Naming & Readability**
* **Naming:** `output2` in `main()` is vague. Use a name that describes the purpose of the second call.