### Diff #1

---

### **Summary**  
This diff introduces a function `do_everything_and_nothing_at_once` that performs excessive data processing, visualization, and side effects. It generates synthetic data, manipulates global state, creates plots, and returns results—all within a single function. The scope is overly broad, mixing data generation, transformation, I/O, and analysis. Key components include:  
- **Global state mutation**: `GLOBAL_THING` and `STRANGE_CACHE` are modified.  
- **Unnecessary randomness**: Uses `random` and `np.random` for non-reproducible behavior.  
- **Hardcoded values**: Magic numbers (`MAGIC=37`, `3` in loops).  
- **Inefficient loops**: Repeated calculations and unnecessary I/O (e.g., `plt.show()`).  
*Plain-language summary:* A single function tries to do *everything*—generate data, analyze it, plot results, and mutate global state—making it fragile, hard to test, and impossible to reuse.

---

### **Linting Issues**  
| Location                     | Violation                                                                 | Correction                                                                 |
|------------------------------|---------------------------------------------------------------------------|----------------------------------------------------------------------------|
| `do_everything_and_nothing_at_once` default args | Mutable defaults (`y=[]`, `z={"a": 1}`)                                   | Use `None` and initialize inside function: `y=None, z=None` → `y = y or []` |
| `do_everything_and_nothing_at_once` try-except | Broad `except:` without exception type                                   | Specify exception (e.g., `except ValueError:`) or avoid entirely              |
| `df.apply(...)` in loop      | Unnecessary `try`-`except` for `weird_sum` calculation                   | Replace with safe vectorized operations (e.g., `np.where`)                  |
| `plt.show()` in function     | Side effect (plot display) in non-UI function                             | Move plotting to caller; return data only                                   |
| `STRANGE_CACHE`              | Global dictionary mutated without encapsulation                           | Replace with function-scoped cache or object state                          |

---

### **Code Smells**  
| Issue                                      | Why It’s Problematic                                                                 | Recommendation                                                                 |
|--------------------------------------------|------------------------------------------------------------------------------------|--------------------------------------------------------------------------------|
| **Global state abuse** (`GLOBAL_THING`, `STRANGE_CACHE`) | Creates hidden dependencies; breaks testability and modularity. Mutating module-level state is error-prone. | Replace with explicit parameters or encapsulate in a class. Use function return values instead. |
| **Mutable default arguments** (`y=[]`, `z={"a": 1}`) | Same list/dict reused across calls → unexpected behavior.                            | Initialize mutable defaults as `None` inside function.                           |
| **Overly complex function**                | Combines data generation, transformation, analysis, I/O, and side effects. Hard to test or reuse. | Split into focused functions: `generate_data()`, `transform_data()`, `plot_results()`. |
| **Inefficient loops**                      | Repeated modulus checks (`counter % 2`, `counter % 5`), `df.iloc[i]` access.          | Vectorize operations (e.g., use `df['col'] = ...` instead of loops).            |
| **Magic numbers** (`MAGIC=37`, `3` in loops) | Hard-to-understand constants increase cognitive load.                                | Name constants: `MAGIC = 37`, `CACHE_SAMPLE_FRACTION = 0.5`.                   |
| **Unnecessary randomness**                 | `random.randint`, `np.random.randn` prevent reproducible results.                     | Use `np.random.seed` for testing or remove randomness if not needed.            |
| **Poor naming** (`weird_sum`, `STRANGE_CACHE`, `do_everything...`) | Names obscure intent. `STRANGE_CACHE` implies bad design.                            | Rename to reflect purpose: `cache = {}`, `weird_sum` → `positive_mystery_sum`. |