## Diff #1

### Summary
This PR introduces a basic data processing module that handles item processing with caching and side-effect operations. It includes functions like `process_items`, `expensive_compute`, and `get_user_data`. The main execution flow uses a loop over items, applies caching logic, performs delayed computation via sleep, and prints outputs. This change modifies core behavior by introducing global state (`cache`, `results`) and relies on mutable defaults and side effects.

### Linting Issues
- **Mutable Default Argument**: Function `process_items(items=[], verbose=False)` uses a mutable default argument (`[]`). This can cause unexpected behavior due to shared state across calls.
  - ✅ **Fix**: Replace `items=[]` with `items=None` and initialize inside function body.
- **Redundant List Comprehension Syntax**: Line `[results.append(cache[item])]` unnecessarily wraps a statement in a list comprehension syntax.
  - ✅ **Fix**: Use direct `results.append(cache[item])`.
- **Global State Usage**: Global variables `cache` and `results` are modified without clear encapsulation.
  - ✅ **Fix**: Consider passing these explicitly or using local scopes.

### Code Smells
- **Side Effects in List Comprehension**: The use of `[results.append(...)]` suggests misuse of list comprehension for side effects.
  - ❌ **Problem**: Misuse of Python constructs leads to confusion and reduces readability.
  - 💡 **Recommendation**: Replace with explicit loop or inline append.
- **Inefficient Caching Strategy**: Caching logic does not consider concurrency or invalidation.
  - ❌ **Problem**: Potential race conditions and stale data in multi-threaded environments.
  - 💡 **Recommendation**: Introduce proper locking or cache invalidation strategy.
- **Magic Numbers/Strings**: Hardcoded values such as `0.01` (sleep duration), `"invalid"`, `"Lots of results!"` reduce flexibility and clarity.
  - ❌ **Problem**: Difficult to tune or reuse.
  - 💡 **Recommendation**: Extract constants or make configurable.

---