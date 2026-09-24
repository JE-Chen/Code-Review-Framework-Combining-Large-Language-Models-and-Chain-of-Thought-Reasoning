### Code Review

#### 1. Readability & Consistency
- **Naming Conventions**: Function and variable names are non-descriptive and unprofessional (e.g., `do_everything_and_nothing_at_once`, `GLOBAL_THING`, `STRANGE_CACHE`, `weird_sum`, `something_useless`). These should be renamed to reflect their actual business or technical purpose.
- **Formatting**: The code generally follows PEP 8, but the logic is cluttered and lacks comments explaining the intent of the transformations.

#### 2. Software Engineering Standards
- **Modularization**: The function `do_everything_and_nothing_at_once` violates the Single Responsibility Principle. It handles data generation, transformation, statistical analysis, caching, and visualization. This should be split into at least four distinct functions.
- **Mutable Default Arguments**: The function signature `do_everything_and_nothing_at_once(x=None, y=[], z={"a": 1})` uses mutable defaults (`[]` and `{}`). In Python, these are shared across all calls to the function, which can lead to unexpected behavior. Use `None` and initialize inside the function.
- **Global State**: The use of `global GLOBAL_THING` and the `STRANGE_CACHE` global dictionary makes the code difficult to test and thread-unsafe.

#### 3. Logic & Correctness
- **Exception Handling**: 
    - There are several "bare except" blocks (e.g., `except: pass` and `except Exception as e: weird_sum += 0`). This hides potential bugs and makes debugging nearly impossible.
    - The `try...except` around `float(str(value))` is redundant as `value` is already a float or int.
- **Inefficient Iteration**: The loop `for i in range(len(df)):` using `df.iloc[i]` is an anti-pattern in pandas. This should be replaced with vectorized operations (e.g., `np.where` or `.sum()`) for significantly better performance.

#### 4. Performance & Security
- **Pandas Performance**: The use of `.apply(lambda row: ... axis=1)` is slow. This logic can be implemented using vectorized pandas/numpy operations.
- **Resource Management**: `plt.show()` is called inside the function, which blocks execution until the window is closed. This is unsuitable for automated pipelines or library code.

#### 5. RAG Rules (Deterministic Logic)
- **Non-Deterministic Logic**: The code contains direct calls to `random.randint`, `random.random`, `np.random.randn`, and `df.sample`. These are not isolated or seeded, making the output non-deterministic and tests impossible to reproduce.
- **Time Dependency**: The call to `time.sleep(0.01)` is an arbitrary delay that serves no functional purpose and slows down execution.

#### 6. Documentation & Testing
- **Missing Documentation**: There are no docstrings explaining the inputs, outputs, or the purpose of the calculations.
- **Testing**: No unit tests are provided. Given the complexity and randomness of the logic, tests are critical.

---

### Summary of Recommendations
1. **Refactor** the monolithic function into smaller, focused functions.
2. **Replace** all global variables with return values or class attributes.
3. **Vectorize** pandas operations to remove `iloc` loops and `apply(axis=1)`.
4. **Fix** mutable default arguments in the function signature.
5. **Isolate** randomness and time calls to allow for deterministic testing.
6. **Replace** bare `except` blocks with specific exception handling.