### Code Review

**Naming Conventions**
* `meanVal`: Use `snake_case` (`mean_val`) to maintain consistency with Python (PEP 8) and the rest of the codebase.

**Software Engineering Standards**
* **Global State**: The use of `global DATA` and `global RESULTS` makes the application stateful and not thread-safe. In a production Flask environment (with multiple workers), this will lead to inconsistent data across requests.
* **Redundant Logic**: `statistics.mean(DATA)` is called twice and assigned to two different keys (`mean` and `meanAgain`). This is unnecessary duplication.
* **Redundant Logic**: `statistics.median(DATA)` is called twice and assigned to two different keys (`median` and `medianPlus42`).

**Logic & Correctness**
* **State Persistence**: The `RESULTS` dictionary is never cleared when `/generate` is called. If a user generates new data and then calls `/analyze`, the `RESULTS` dictionary will contain a mix of old and new calculations.

**Performance & Security**
* **Debug Mode**: `app.run(debug=True)` is enabled. This should be disabled or moved to an environment variable for production to avoid exposing sensitive traceback information.

**Suggestions for Improvement**
* Replace global variables with a database or a caching layer (e.g., Redis) for state management.
* Store the result of `statistics.mean()` and `statistics.median()` in a local variable before assigning them to the dictionary to avoid redundant computations.
* Reset `RESULTS` inside the `/generate` route to ensure analysis is performed on the current dataset.