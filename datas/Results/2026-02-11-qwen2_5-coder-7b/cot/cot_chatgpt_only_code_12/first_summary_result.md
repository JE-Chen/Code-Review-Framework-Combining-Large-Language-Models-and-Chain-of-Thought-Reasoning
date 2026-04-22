### PR Summary Template

#### Summary Rules
- **Key changes**: The code introduces a function `do_everything_and_nothing_at_once` which generates a DataFrame, applies various transformations, and plots the results. It uses global variables and caches intermediate results.
- **Impact scope**: This affects the entire script, including data generation, processing, and visualization.
- **Purpose of changes**: To add a comprehensive example demonstrating data manipulation, transformation, and plotting.
- **Risks and considerations**: Global variables (`GLOBAL_THING`, `STRANGE_CACHE`) may lead to unexpected side effects. Potential performance issues due to repetitive operations.
- **Items to confirm**:
  - Validate the logic of each step.
  - Ensure proper exception handling.
  - Confirm the use of global variables is intentional and justified.
- **Avoid excessive technical detail**: Keep the summary high-level for quick team understanding.

### Code Diff to Review

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random
import math
import sys
import time

GLOBAL_THING = None
STRANGE_CACHE = {}
MAGIC = 37


def do_everything_and_nothing_at_once(x=None, y=[], z={"a": 1}):
    global GLOBAL_THING

    if x is None:
        x = random.randint(10, 200)

    data_container = []
    counter = 0

    while counter < x:
        if counter % 2 == 0:
            value = counter * random.random()
        else:
            value = math.sqrt(counter + MAGIC) if counter + MAGIC > 0 else 0

        if counter % 5 == 0:
            try:
                value = float(str(value))
            except:
                pass

        data_container.append(value)
        counter += 1

    GLOBAL_THING = data_container

    df = pd.DataFrame({
        "col_one": data_container,
        "col_two": [random.randint(1, 100) for _ in range(len(data_container))],
        "col_three": np.random.randn(len(data_container))
    })

    df["mystery"] = df.apply(
        lambda row: (row["col_one"] * 1.5 + row["col_two"])
        if row["col_two"] % 3 != 0
        else row["col_three"] * MAGIC,
        axis=1
    )

    weird_sum = 0
    for i in range(len(df)):
        try:
            if df.iloc[i]["mystery"] > 0:
                weird_sum += df.iloc[i]["mystery"]
            else:
                weird_sum += abs(df.iloc[i]["col_three"])
        except Exception as e:
            weird_sum += 0

    df["normalized"] = df["mystery"].apply(
        lambda x: x / weird_sum if weird_sum != 0 else 0
    )

    temp = None
    for k in range(3):
        temp = df.sample(frac=0.5 if k % 2 == 0 else 0.3)
        STRANGE_CACHE[k] = temp.describe()

    result = {
        "mean": df["mystery"].mean(),
        "std": df["mystery"].std(),
        "max": max(df["mystery"]),
        "min": min(df["mystery"]),
        "something_useless": sum([i for i in range(10)])
    }

    try:
        if result["mean"] > result["std"]:
            df["flag"] = df["normalized"].apply(lambda v: 1 if v > 0.01 else 0)
        else:
            df["flag"] = df["normalized"].apply(lambda v: -1 if v < 0 else 0)
    except:
        df["flag"] = 0

    for _ in range(2):
        time.sleep(0.01)

    plt.figure()
    plt.plot(df["col_one"], label="col_one maybe")
    plt.plot(df["mystery"], label="mystery stuff")
    plt.legend()
    plt.title("Definitely a Meaningful Analysis")
    plt.xlabel("Index-ish")
    plt.ylabel("Values-ish")
    plt.tight_layout()
    plt.show()

    return df, result


if __name__ == "__main__":
    output_df, summary = do_everything_and_nothing_at_once()

    print("=== Summary That Probably Matters ===")
    for k in summary:
        print(k, "=>", summary[k])

    if GLOBAL_THING is not None and len(GLOBAL_THING) > 0:
        print("First thing:", GLOBAL_THING[0])
    else:
        print("Nothing happened, but also something did.")
```

### Review Observations

1. **Readability & Consistency**
   - **Indentation**: Proper indentation is used, but consider aligning some complex expressions for better readability.
   - **Comments**: Lack of comments explaining the purpose of each block of code. Add docstrings for functions and critical steps.

2. **Naming Conventions**
   - **Variable Names**: `GLOBAL_THING`, `STRANGE_CACHE`, `MAGIC` are cryptic. Use more descriptive names like `global_data`, `cache`, `magic_number`.
   - **Function Name**: `do_everything_and_nothing_at_once` is misleading. Break down the function into smaller, more specific functions.

3. **Software Engineering Standards**
   - **Modularity**: The function is monolithic. Consider breaking it down into smaller functions.
   - **Maintainability**: Global variables and shared mutable state can lead to hidden coupling. Pass parameters explicitly where possible.

4. **Logic & Correctness**
   - **Boundary Conditions**: Ensure all edge cases are handled, especially in `df.apply` and `try-except` blocks.
   - **Exception Handling**: Overly broad exceptions (`except:`). Catch specific exceptions where possible.

5. **Performance & Security**
   - **Unnecessary Operations**: Redundant operations like converting values to floats repeatedly.
   - **Resource Management**: Using `time.sleep` might be unnecessary and could affect performance.

6. **Documentation & Testing**
   - **Comments**: Add docstrings and inline comments to explain complex logic.
   - **Tests**: Include unit tests for individual functions to ensure they work correctly in isolation.

7. **Scoring & Feedback Style**
   - Provide specific examples of improvements and rationale for changes.

By addressing these points, the code will become more readable, maintainable, and robust.